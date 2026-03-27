# ParBench — CPU-only validation image
# Purpose: Schema validation, unit tests, analysis scripts, and figure generation.
# This image does NOT include CUDA/GPU support — use host GPU setup for eval runs.
#
# Build:  docker build -t parbench .
# Run:    docker run --rm -it parbench
# Test:   docker run --rm parbench python3 -m pytest c_augmentation/test_transforms.py -v
# Validate: docker run --rm parbench python3 scripts/validate_schema.py --all

FROM python:3.12-slim

# System dependencies for libclang
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libclang-dev \
        gcc \
        g++ \
        make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies (lock file for exact reproducibility)
COPY requirements-lock.txt .
RUN pip install --no-cache-dir -r requirements-lock.txt

# Copy project source
COPY pyproject.toml .
COPY harness/ harness/
COPY c_augmentation/ c_augmentation/
COPY scripts/ scripts/
COPY schema/ schema/
COPY specs/ specs/
COPY manifest.jsonl .
COPY config/ config/

# Fix paths.json for container (host paths won't exist)
RUN python3 -c "import json; p='/app'; json.dump({'project_root':p,'downloads_root':p,'hecbench_root':p}, open('config/paths.json','w'), indent=4)"

# Install project in editable mode (registers harness and c_augmentation packages)
RUN pip install --no-cache-dir -e .

# Default: run schema validation
CMD ["python3", "scripts/validate_schema.py", "--all"]
