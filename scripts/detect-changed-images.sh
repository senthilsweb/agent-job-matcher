#!/usr/bin/env bash
# File Name: detect-changed-images.sh
# Author: Senthilnathan Karuppaiah
# Date: 26-SEP-2026
# Description:
# Decides which Docker images the "Build & publish" workflow must build,
# so a change to one component does not rebuild the others.
#
# This script works by:
# 1. Listing the files changed in the git range given as $1 (for example
#    "base...head" on a pull request, "before..after" on a push).
# 2. Matching each file against every image's path patterns, defined once
#    in COMPONENTS below — this table is the only place to edit when an
#    image's inputs change or a new image is added.
# 3. Printing a JSON array of the matching {image, context, dockerfile}
#    entries on stdout, ready for a GitHub Actions matrix. "[]" means
#    nothing needs building.
# 4. Building EVERYTHING when the range is empty or cannot be resolved
#    (tag pushes, manual runs, brand-new branches, force pushes), or when
#    the workflow or this script itself changed. Failing safe means a
#    wrong guess costs build minutes, never a stale image.
#
# Requirements:
# - bash 3.2+ and git (no jq: the JSON is assembled by hand)
#
# Usage:
#   scripts/detect-changed-images.sh "<git range>"     # "" builds everything
#
# Environment Variables: none.

set -euo pipefail

RANGE="${1:-}"

# Table: image ; build context ; dockerfile ; extended regex of files that feed the image.
# The backend image and the agent service both install ./backend, so backend/ feeds both.
COMPONENTS=(
  "senthilsweb/agent-job-matcher;.;./Dockerfile;^(backend/|Dockerfile$|\.dockerignore$)"
  "senthilsweb/agent-job-matcher-agent-service;.;./mcp/agent-service/Dockerfile;^(backend/|mcp/|\.dockerignore$)"
  "senthilsweb/agent-job-matcher-playground;./playground;./playground/Dockerfile;^playground/"
  "senthilsweb/agent-job-matcher-openapi-docs;./openapi-docs;./openapi-docs/Dockerfile;^openapi-docs/"
)

# Files whose change means "rebuild everything": the build definition itself.
BUILD_ALL_REGEX='^(\.github/workflows/build-and-publish\.yml|scripts/detect-changed-images\.sh)$'

# Emit one component as a JSON object.
entry() {
  local image context dockerfile _
  IFS=';' read -r image context dockerfile _ <<<"$1"
  printf '{"image":"%s","context":"%s","dockerfile":"%s"}' "$image" "$context" "$dockerfile"
}

# Emit the JSON array for the components whose indices are passed as arguments.
emit() {
  local out="" idx
  for idx in "$@"; do
    [ -n "$out" ] && out+=","
    out+="$(entry "${COMPONENTS[$idx]}")"
  done
  printf '[%s]\n' "$out"
}

ALL_INDICES=()
for i in "${!COMPONENTS[@]}"; do ALL_INDICES+=("$i"); done

# No range, or a range git cannot resolve: build everything.
if [ -z "$RANGE" ] || ! CHANGED="$(git diff --name-only "$RANGE" 2>/dev/null)"; then
  emit "${ALL_INDICES[@]}"
  exit 0
fi

# The build definition changed: build everything so the change is exercised.
if printf '%s\n' "$CHANGED" | grep -Eq "$BUILD_ALL_REGEX"; then
  emit "${ALL_INDICES[@]}"
  exit 0
fi

# Otherwise select only the components whose inputs changed.
SELECTED=()
for i in "${!COMPONENTS[@]}"; do
  IFS=';' read -r _ _ _ regex <<<"${COMPONENTS[$i]}"
  if printf '%s\n' "$CHANGED" | grep -Eq "$regex"; then
    SELECTED+=("$i")
  fi
done

if [ "${#SELECTED[@]}" -eq 0 ]; then
  echo "[]"
else
  emit "${SELECTED[@]}"
fi
