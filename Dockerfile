FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN if [ "$(uname -m)" = "i686" ] || [ "$(uname -m)" = "i386" ] || [ "$(uname -m)" = "x86" ]; then \
        apt-get update \
        && apt-get install -y --no-install-recommends gcc libc6-dev make zlib1g-dev libjpeg62-turbo-dev libfreetype6-dev \
        && rm -rf /var/lib/apt/lists/*; \
    fi

RUN pip install django==6.1 djangorestframework drf-spectacular reportlab

RUN if [ "$(uname -m)" = "i686" ] || [ "$(uname -m)" = "i386" ] || [ "$(uname -m)" = "x86" ]; then \
        apt-get purge -y gcc libc6-dev make zlib1g-dev libjpeg62-turbo-dev libfreetype6-dev \
        && apt-get install -y --no-install-recommends libjpeg62-turbo libfreetype6 zlib1g \
        && apt-get autoremove -y \
        && rm -rf /var/lib/apt/lists/*; \
    fi

RUN python -c "\
import platform, urllib.request; \
asset = {'x86_64':'amd64','aarch64':'arm64','i686':'386','i386':'386','x86':'386','armv7l':'armhf','armv6l':'arm','ppc64le':'ppc64le','s390x':'s390x'}.get(platform.machine(), platform.machine()); \
urllib.request.urlretrieve(f'https://github.com/cloudflare/cloudflared/releases/download/2026.3.0/cloudflared-linux-{asset}', '/usr/local/bin/cloudflared'); \
" \
    && chmod +x /usr/local/bin/cloudflared

COPY WebApp/ ./WebApp/
COPY entrypoint.sh /entrypoint.sh

RUN rm -f WebApp/db.sqlite3 WebApp/*.pdf \
    && chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
