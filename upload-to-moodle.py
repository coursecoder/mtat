#!/usr/bin/env python3
"""
MTAT — upload-to-moodle.py

Reads generated variants from variants/manifest.yaml and uploads them to a
local Moodle instance as a course with one Book activity per module. Each
audience variant becomes a chapter inside that Book, so you can flip between
developer / executive / champion / technical-writer views side-by-side.

Prerequisites:
  1. Moodle running: docker compose up -d
  2. Wait ~2 min for first-run init, then visit http://localhost:8080
  3. Moodle REST API must be enabled (this script does it automatically via CLI
     inside the container, or follow the manual steps in the README).
  4. Virtual env active with dependencies installed:
       pip install -r requirements.txt

Usage:
  # Upload all variants in manifest.yaml to Moodle
  python upload-to-moodle.py

  # Upload a specific course ID only
  python upload-to-moodle.py --course-id prompt-engineering-fundamentals

  # Point at a non-default Moodle URL or token
  python upload-to-moodle.py --url http://localhost:8080 --token <token>

  # Print the Moodle token (useful after first run)
  python upload-to-moodle.py --get-token
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import markdown
import requests
import yaml

# ---------------------------------------------------------------------------
# Config defaults
# ---------------------------------------------------------------------------

DEFAULT_URL = "http://localhost:8080"
DEFAULT_USER = "admin"
DEFAULT_PASS = ""  # Set via --password flag or MOODLE_ADMIN_PASS env var
TOKEN_CACHE_FILE = Path(".moodle-token")

# ---------------------------------------------------------------------------
# Moodle REST helpers
# ---------------------------------------------------------------------------


def api(url: str, token: str, function: str, **params) -> dict:
    """Call a Moodle Web Services REST function. Raises on HTTP or API error."""
    resp = requests.post(
        f"{url}/webservice/rest/server.php",
        data={
            "wstoken": token,
            "moodlewsrestformat": "json",
            "wsfunction": function,
            **params,
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, dict) and "exception" in data:
        raise RuntimeError(f"Moodle API error [{function}]: {data.get('message', data)}")
    return data


# ---------------------------------------------------------------------------
# First-time Moodle setup via docker exec
# ---------------------------------------------------------------------------

MOODLE_CLI_SCRIPT = """\
<?php
// Enable web services + REST protocol + create external service + add token
define('CLI_SCRIPT', true);
require('/bitnami/moodle/config.php');
require_once($CFG->libdir . '/adminlib.php');
require_once($CFG->dirroot . '/webservice/lib.php');

// 1. Enable web services globally
set_config('enablewebservices', 1);

// 2. Enable REST protocol
$protos = get_config('core', 'webserviceprotocols');
$protos_arr = $protos ? explode(',', $protos) : [];
if (!in_array('rest', $protos_arr)) {
    $protos_arr[] = 'rest';
    set_config('webserviceprotocols', implode(',', $protos_arr));
}

// 3. Create external service 'mtat_upload' if it doesn't exist
$DB->delete_records('external_services', ['shortname' => 'mtat_upload']);
$service = new stdClass();
$service->name = 'MTAT Upload';
$service->shortname = 'mtat_upload';
$service->enabled = 1;
$service->restrictedusers = 0;
$service->downloadfiles = 0;
$service->uploadfiles = 0;
$service->timecreated = time();
$service->timemodified = time();
$sid = $DB->insert_record('external_services', $service);

// 4. Add required functions to the service
$functions = [
    'core_course_create_courses',
    'core_course_get_courses_by_field',
    'mod_book_get_books_by_courses',
    'core_course_get_contents',
    'core_webservice_get_site_info',
    'mod_book_view_book',
];
foreach ($functions as $fname) {
    $rec = new stdClass();
    $rec->externalserviceid = $sid;
    $rec->functionname = $fname;
    $DB->insert_record('external_services_functions', $rec);
}

// 5. Create a token for admin user (userid=2 is always admin in fresh Moodle)
$DB->delete_records('external_tokens', ['externalserviceid' => $sid]);
$token = new stdClass();
$token->token = md5(uniqid(rand(), true));
$token->tokentype = EXTERNAL_TOKEN_PERMANENT;
$token->userid = 2;
$token->externalserviceid = $sid;
$token->contextid = context_system::instance()->id;
$token->creatorid = 2;
$token->timecreated = time();
$token->validuntil = 0;
$token->iprestriction = null;
$DB->insert_record('external_tokens', $token);

echo $token->token . PHP_EOL;
"""


def setup_moodle_webservices(container: str = "mtat-moodle") -> str:
    """
    Run a PHP CLI script inside the Moodle container to enable REST web
    services and create an API token. Returns the token string.
    """
    print("Setting up Moodle web services (requires Docker)...")

    # Write the PHP script to a temp file inside the container
    script_path = "/tmp/mtat_setup.php"
    try:
        subprocess.run(
            ["docker", "exec", container, "bash", "-c",
             f"cat > {script_path} << 'PHPEOF'\n{MOODLE_CLI_SCRIPT}\nPHPEOF"],
            check=True, capture_output=True,
        )
        result = subprocess.run(
            ["docker", "exec", container, "php", script_path],
            check=True, capture_output=True, text=True,
        )
        token = result.stdout.strip().splitlines()[-1]
        if not re.match(r"^[0-9a-f]{32}$", token):
            raise RuntimeError(f"Unexpected PHP output: {result.stdout!r}")
        print(f"  Web services enabled. Token: {token}")
        return token
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"docker exec failed: {e.stderr}\n"
            "Is the container running? Try: docker compose up -d"
        ) from e


def wait_for_moodle(url: str, timeout: int = 180):
    """Poll until Moodle's login page responds (first-run init can take 2+ min)."""
    print(f"Waiting for Moodle at {url} ", end="", flush=True)
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(f"{url}/login/index.php", timeout=5)
            if r.status_code == 200:
                print(" ready.")
                return
        except requests.RequestException:
            pass
        print(".", end="", flush=True)
        time.sleep(5)
    raise TimeoutError(f"Moodle did not become ready within {timeout}s.")


# ---------------------------------------------------------------------------
# Course + Book creation helpers
# ---------------------------------------------------------------------------

CATEGORY_ID = 1  # "Miscellaneous" — always exists on a fresh Moodle


def ensure_course(url: str, token: str, course_id: str, course_title: str) -> int:
    """Return Moodle internal course id, creating it if it doesn't exist."""
    existing = api(url, token, "core_course_get_courses_by_field",
                   field="idnumber", value=course_id)
    courses = existing.get("courses", [])
    if courses:
        moodle_id = courses[0]["id"]
        print(f"  Course already exists (id={moodle_id}): {course_title}")
        return moodle_id

    created = api(url, token, "core_course_create_courses",
                  **{
                      "courses[0][fullname]": course_title,
                      "courses[0][shortname]": course_id[:100],
                      "courses[0][idnumber]": course_id,
                      "courses[0][categoryid]": CATEGORY_ID,
                      "courses[0][summary]": f"Auto-generated by MTAT upload script.",
                      "courses[0][summaryformat]": 1,
                      "courses[0][format]": "topics",
                      "courses[0][visible]": 1,
                  })
    moodle_id = created[0]["id"]
    print(f"  Created course (id={moodle_id}): {course_title}")
    return moodle_id


def md_to_html(md_text: str) -> str:
    """Convert Markdown (with fenced code blocks) to HTML."""
    return markdown.markdown(
        md_text,
        extensions=["fenced_code", "tables", "nl2br", "sane_lists"],
    )


def strip_front_matter(text: str) -> str:
    """Remove YAML front matter block if present."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:].lstrip()
    return text


def upload_variants_to_book(
    url: str,
    token: str,
    course_moodle_id: int,
    module_title: str,
    variants: list[dict],
    manifest_dir: Path,
):
    """
    For a given module, upload one Page resource per audience variant into the course.
    """
    print(f"\n  Module: {module_title} ({len(variants)} variants)")

    for i, variant in enumerate(variants, start=1):
        variant_path = manifest_dir / variant["output_file"]
        if not variant_path.exists():
            print(f"    [!] Variant file not found, skipping: {variant_path}")
            continue

        raw_md = variant_path.read_text(encoding="utf-8")
        body_md = strip_front_matter(raw_md)
        html = md_to_html(body_md)

        audience = variant.get("audience", "unknown")
        locale = variant.get("locale", "en-US")
        page_title = f"{module_title} [{audience} / {locale}]"

        _create_page_resource(url, course_moodle_id, page_title, html, DEFAULT_USER, DEFAULT_PASS)
        print(f"    + Uploaded: {page_title}")

    print(f"  Done. Open your course at: {url}/course/view.php?id={course_moodle_id}")


def _create_page_resource(
    url: str, course_id: int, title: str, html_content: str, username: str, password: str
):
    """
    Create a Moodle Page resource via a session-authenticated form POST.
    The REST API doesn't expose mod_page_add_page, so we use the web form.
    """
    session = requests.Session()

    # Log in to get a session cookie
    login_page = session.get(f"{url}/login/index.php", timeout=10)
    # Extract logintoken from the form
    match = re.search(r'name="logintoken" value="([^"]+)"', login_page.text)
    logintoken = match.group(1) if match else ""

    session.post(
        f"{url}/login/index.php",
        data={
            "username": username,
            "password": password,
            "logintoken": logintoken,
        },
        timeout=10,
        allow_redirects=True,
    )

    # Get the "Add Page" form to extract sesskey and other hidden fields
    add_page = session.get(
        f"{url}/course/modedit.php",
        params={"add": "page", "type": "", "course": course_id, "section": 0},
        timeout=10,
    )
    sesskey_match = re.search(r'"sesskey":"([^"]+)"', add_page.text)
    sesskey = sesskey_match.group(1) if sesskey_match else ""

    # Submit the Page creation form
    session.post(
        f"{url}/course/modedit.php",
        data={
            "sesskey": sesskey,
            "add": "page",
            "course": course_id,
            "section": 0,
            "name": title,
            "intro": "",
            "introformat": 1,
            "page[text]": html_content,
            "page[format]": 1,
            "submitbutton2": "Save and return to course",
            "mform_isexpanded_id_generalhdr": 1,
        },
        timeout=30,
        allow_redirects=True,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def load_manifest(manifest_path: Path) -> list[dict]:
    if not manifest_path.exists():
        print(f"No manifest found at {manifest_path}.")
        print("Generate variants first: python generate-variant.py --module example-course/01-concept --audience developer")
        sys.exit(1)
    with manifest_path.open() as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, list) else []


def group_by_course(entries: list[dict]) -> dict[str, dict]:
    """
    Returns { course_id: { title, modules: { module_id: [variant, ...] } } }
    Infers course title from module metadata where available.
    """
    courses: dict[str, dict] = {}
    for entry in entries:
        course_id = entry.get("course_id", "mtat-preview")
        if course_id not in courses:
            courses[course_id] = {
                "title": course_id.replace("-", " ").title(),
                "modules": {},
            }
        mod_id = entry.get("module_id", entry.get("module_path", "unknown"))
        courses[course_id]["modules"].setdefault(mod_id, []).append(entry)
    return courses


def main():
    global DEFAULT_USER, DEFAULT_PASS
    parser = argparse.ArgumentParser(
        description="Upload MTAT variants to a local Moodle instance."
    )
    parser.add_argument("--url", default=DEFAULT_URL, help="Moodle base URL (default: http://localhost:8080)")
    parser.add_argument("--token", default=None, help="Moodle API token (skips auto-setup if provided)")
    parser.add_argument("--user", default=DEFAULT_USER, help="Moodle admin username (default: admin)")
    parser.add_argument("--password", default=os.environ.get("MOODLE_ADMIN_PASS", ""), help="Moodle admin password (or set MOODLE_ADMIN_PASS env var)")
    parser.add_argument("--course-id", default=None, help="Only upload variants for this course ID")
    parser.add_argument("--manifest", default="variants/manifest.yaml", help="Path to manifest.yaml")
    parser.add_argument("--setup-moodle", action="store_true", help="Run first-time Moodle web-services setup via docker exec")
    parser.add_argument("--get-token", action="store_true", help="Print the cached/generated token and exit")
    args = parser.parse_args()

    # Patch module-level defaults so helper functions pick up CLI values
    DEFAULT_USER = args.user
    DEFAULT_PASS = args.password

    manifest_path = Path(args.manifest)
    manifest_dir = manifest_path.parent.parent  # project root

    # ---- Token resolution ----
    token = args.token

    if not token and TOKEN_CACHE_FILE.exists():
        token = TOKEN_CACHE_FILE.read_text().strip()

    if not token or args.setup_moodle:
        wait_for_moodle(args.url)
        token = setup_moodle_webservices()
        TOKEN_CACHE_FILE.write_text(token)
        print(f"Token cached to {TOKEN_CACHE_FILE}")

    if args.get_token:
        print(token)
        return

    # Verify token works
    try:
        site = api(args.url, token, "core_webservice_get_site_info")
        print(f"Connected to Moodle: {site.get('sitename')} (Moodle {site.get('release', '?')})")
    except Exception as e:
        print(f"Token validation failed: {e}")
        print("Try running with --setup-moodle to regenerate the token.")
        sys.exit(1)

    # ---- Load manifest ----
    entries = load_manifest(manifest_path)
    if not entries:
        print("Manifest is empty — nothing to upload.")
        sys.exit(0)

    # ---- Filter by course if requested ----
    if args.course_id:
        entries = [e for e in entries if e.get("course_id") == args.course_id]
        if not entries:
            print(f"No variants found for course_id='{args.course_id}'")
            sys.exit(1)

    courses = group_by_course(entries)
    print(f"\nUploading {len(entries)} variant(s) across {len(courses)} course(s)...\n")

    for course_id, course_data in courses.items():
        print(f"Course: {course_data['title']} ({course_id})")
        moodle_course_id = ensure_course(args.url, token, course_id, course_data["title"])

        for module_id, variants in course_data["modules"].items():
            # Try to get a human title from the first variant's module path
            module_title = module_id
            if variants:
                mod_path = Path(variants[0].get("module_path", ""))
                meta_file = manifest_dir / mod_path / "metadata.yaml"
                if meta_file.exists():
                    meta = yaml.safe_load(meta_file.read_text())
                    module_title = meta.get("title", module_id)

            upload_variants_to_book(
                args.url, token, moodle_course_id,
                module_title, variants, manifest_dir,
            )

    print("\nAll done.")
    print(f"Open Moodle: {args.url}/my/courses.php")


if __name__ == "__main__":
    main()
