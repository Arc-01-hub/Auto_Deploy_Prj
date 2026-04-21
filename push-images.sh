#!/usr/bin/env bash
set -euo pipefail

DOCKERHUB_USERNAME="laloperly"
IMAGE_NAME="auto_deploy_prj"
TAG="${1:-latest}"
FULL_IMAGE="${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${TAG}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

echo "Building ${FULL_IMAGE}..."
docker build -t "${FULL_IMAGE}" .

echo "Pushing ${FULL_IMAGE}..."
docker push "${FULL_IMAGE}"

if [[ "${TAG}" != "latest" ]]; then
  LATEST_IMAGE="${DOCKERHUB_USERNAME}/${IMAGE_NAME}:latest"
  echo "Tagging and pushing ${LATEST_IMAGE}..."
  docker tag "${FULL_IMAGE}" "${LATEST_IMAGE}"
  docker push "${LATEST_IMAGE}"
fi

echo "Done."
