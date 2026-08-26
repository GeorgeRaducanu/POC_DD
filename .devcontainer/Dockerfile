FROM mcr.microsoft.com/devcontainers/cpp:1-debian-12

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        cmake \
        doxygen \
        graphviz \
        libclang-dev \
        ninja-build \
        clang \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

COPY utils/gen_dd/requirements.txt /tmp/gen-dd-requirements.txt
RUN python3 -m pip install --break-system-packages -r /tmp/gen-dd-requirements.txt \
    && rm /tmp/gen-dd-requirements.txt

USER vscode