# Loam's mutation-sweep image (docs/factory/LOOP.md, Mutation sweep): every pytest run of a sweep on Loam runs in a
# container of it, so it holds Loam's test tools: python3, pytest, bash, git, jq and flock (util-linux).
# bin/factory.d/sweep-image builds it as loam-sweep for Loam's launch lines.
FROM python:3.12-slim
RUN apt-get update -q && apt-get install -y -q --no-install-recommends git jq \
 && rm -rf /var/lib/apt/lists/* && pip install -q --no-cache-dir pytest
