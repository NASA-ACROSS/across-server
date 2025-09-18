#!/usr/bin/env bash
set -euo pipefail

# run from repo root
REPO_ROOT="$(pwd)"
TEST_DIR=".github/actions/run-ecspresso/test"
# possible locations for merge.jq (test dir, then parent)
CAND1="$REPO_ROOT/$TEST_DIR/merge.jq"
CAND2="$REPO_ROOT/.github/actions/run-ecspresso/merge.jq"

if [ -f "$CAND1" ]; then
  MERGE_SCRIPT="$CAND1"
elif [ -f "$CAND2" ]; then
  MERGE_SCRIPT="$CAND2"
else
  echo "ERROR: merge.jq not found in either:"
  echo "  $CAND1"
  echo "  $CAND2"
  exit 1
fi

S3="$REPO_ROOT/$TEST_DIR/s3_task_def.json"
INCOMING="$REPO_ROOT/$TEST_DIR/incoming_taskdef.json"
OUT="$REPO_ROOT/$TEST_DIR/merged.json"

for f in "$S3" "$INCOMING" "$MERGE_SCRIPT"; do
  if [ ! -f "$f" ]; then
    echo "ERROR: required file missing: $f"
    exit 1
  fi
done

echo "Using merge.jq: $MERGE_SCRIPT"
echo "S3: $S3"
echo "Incoming: $INCOMING"
echo "Out: $OUT"
echo

run_with_local_jq() {
  echo "Using local jq..."
  jq -s -f "$MERGE_SCRIPT" "$S3" "$INCOMING" > "$OUT"
}

run_with_docker() {
  echo "Local jq not found — using docker (alpine:3.18)..."
  docker run --rm -v "$REPO_ROOT":/work -w /work alpine:3.18 \
    sh -c "apk add --no-cache jq >/dev/null 2>&1 && jq -s -f ${MERGE_SCRIPT#/} ${S3#/} ${INCOMING#/} > ${OUT#/}"
  # note: ${VAR#/} strips leading slash so paths inside container are relative to /work
}

if command -v jq >/dev/null 2>&1; then
  run_with_local_jq
else
  if command -v docker >/dev/null 2>&1; then
    run_with_docker
  else
    echo "ERROR: neither jq nor docker available. Install jq or docker to run this test."
    exit 1
  fi
fi

echo
echo "=== MERGED OUTPUT ==="
if command -v jq >/dev/null 2>&1; then
  jq . "$OUT"
else
  docker run --rm -v "$REPO_ROOT":/work -w /work alpine:3.18 \
    sh -c "apk add --no-cache jq >/dev/null 2>&1 && jq . ${OUT#/}"
fi

echo
echo "=== core-server environment (NAME=VALUE) ==="
if command -v jq >/dev/null 2>&1; then
  jq -r '.containerDefinitions[] | select(.name=="core-server") | (.environment // [])[] | "\(.name)=\(.value)"' "$OUT" | sort
else
  docker run --rm -v "$REPO_ROOT":/work -w /work alpine:3.18 \
    sh -c "apk add --no-cache jq >/dev/null 2>&1 && jq -r '.containerDefinitions[] | select(.name==\"core-server\") | (.environment // [])[] | \"\(.name)=\(.value)\"' ${OUT#/} | sort"
fi

echo
echo "=== DIFF: s3 envs  -> merged envs ==="
TMP_S3=$(mktemp)
TMP_MERGED=$(mktemp)
jq -r '.containerDefinitions[] | select(.name=="core-server") | (.environment // [])[] | "\(.name)=\(.value)"' "$S3" | sort > "$TMP_S3" || true
jq -r '.containerDefinitions[] | select(.name=="core-server") | (.environment // [])[] | "\(.name)=\(.value)"' "$OUT" | sort > "$TMP_MERGED" || true
diff -u "$TMP_S3" "$TMP_MERGED" || true
rm -f "$TMP_S3" "$TMP_MERGED"

echo
echo "Merged file: $OUT"
