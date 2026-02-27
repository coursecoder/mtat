# Builds a complete Moodle 4.3 image on top of the official PHP/Apache base.
# Moodle source is downloaded from GitHub at build time.
FROM moodlehq/moodle-php-apache:8.2

RUN apt-get update && apt-get install -y --no-install-recommends curl tar \
    && rm -rf /var/lib/apt/lists/*

# Download Moodle 4.3 release from GitHub
RUN curl -fsSL \
      https://github.com/moodle/moodle/archive/refs/tags/v4.3.0.tar.gz \
      -o /tmp/moodle.tar.gz \
    && tar -xzf /tmp/moodle.tar.gz -C /tmp \
    && cp -rT /tmp/moodle-4.3.0 /var/www/html \
    && rm -rf /tmp/moodle.tar.gz /tmp/moodle-4.3.0 \
    && chown -R www-data:www-data /var/www/html

# Moodledata directory (writable by Apache)
RUN mkdir -p /var/moodledata && chown www-data:www-data /var/moodledata
