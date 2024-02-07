FROM python

# Pipewire in Docker
# https://stackoverflow.com/a/75776428

RUN \
    apt update && \
    apt install -y \
        pipewire \
        pipewire-alsa \
        alsa-utils \
    && \
    mkdir /.cache /.local && \
    chown 1000:1000 /.cache /.local

USER 1000
WORKDIR /app
COPY ./LocalClient /app

RUN pip install -r /app/requirements.txt

ENTRYPOINT python ./main.py