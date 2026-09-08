FROM registry.access.redhat.com/ubi9/python-311:latest

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    HOME=/workspace/home \
    BOBSERVER_WORKSPACE_ROOT=/workspace \
    PATH=/opt/app-root/src/.local/bin:/opt/app-root/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

WORKDIR /app

USER 0

RUN dnf -y install sqlite openssl findutils && \
    dnf clean all && \
    curl -fsSL https://bob.ibm.com/download/bobshell.sh | bash -s -- --pm npm && \
    mkdir -p /workspace/home /opt/app-root/src && \
    bob --version && \
    chgrp -R 0 /workspace /opt/app-root/src && \
    chmod -R g=u /workspace /opt/app-root/src

COPY pyproject.toml README.md ./
COPY src ./src
COPY scripts ./scripts
COPY skills ./skills
COPY demo ./demo
COPY .bob ./.bob

RUN python3.11 -m pip install --no-cache-dir --upgrade pip && \
    python3.11 -m pip install --no-cache-dir . && \
    mkdir -p /workspace/demo && \
    cp /app/demo/orders_raw.csv /workspace/orders_raw.csv && \
    cp /app/demo/orders.csv /workspace/orders.csv && \
    cp /app/demo/bob_context.md /workspace/bob_context.md && \
    chmod +x /app/scripts/*.sh && \
    /app/scripts/seed-demo-data.sh && \
    chgrp -R 0 /app /workspace && \
    chmod -R g=u /app /workspace

USER 1001:0

EXPOSE 8080

CMD ["/app/scripts/run-api.sh"]
