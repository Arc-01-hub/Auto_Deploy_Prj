#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="${REPO_DIR:-${SCRIPT_DIR}}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
ENV_FILE="${ENV_FILE:-.env.prod}"
DOCKERHUB_USERNAME="${DOCKERHUB_USERNAME:-laloperly}"
IMAGE_TAG="${1:-latest}"

generate_secret() {
  if command -v openssl >/dev/null 2>&1; then
    openssl rand -hex 32
  else
    tr -dc 'a-zA-Z0-9' </dev/urandom | head -c 64
  fi
}

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is not installed. Install Docker first, then re-run this script."
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "Docker Compose plugin is not available. Install docker-compose-plugin, then re-run."
  exit 1
fi

if [[ ! -d "${REPO_DIR}" ]]; then
  echo "Repository directory not found: ${REPO_DIR}"
  exit 1
fi

cd "${REPO_DIR}"

if [[ ! -f "${ENV_FILE}" ]]; then
  MYSQL_PASSWORD="$(generate_secret)"
  FLASK_SECRET="$(generate_secret)"
  cat > "${ENV_FILE}" <<EOF
MYSQL_ROOT_PASSWORD=${MYSQL_PASSWORD}
MYSQL_DATABASE=formations_db
SECRET_KEY=${FLASK_SECRET}
APP_IMAGE_TAG=${IMAGE_TAG}
EOF
  echo "Created ${ENV_FILE} with generated secrets."
fi

if [[ -n "${DOCKERHUB_TOKEN:-}" ]]; then
  echo "${DOCKERHUB_TOKEN}" | docker login -u "${DOCKERHUB_USERNAME}" --password-stdin
fi

if grep -q '^APP_IMAGE_TAG=' "${ENV_FILE}"; then
  sed -i "s/^APP_IMAGE_TAG=.*/APP_IMAGE_TAG=${IMAGE_TAG}/" "${ENV_FILE}"
else
  echo "APP_IMAGE_TAG=${IMAGE_TAG}" >> "${ENV_FILE}"
fi

docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" pull
docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" up -d
docker image prune -f
docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" ps

echo "Deployment complete."
