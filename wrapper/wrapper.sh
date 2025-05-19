#!/usr/bin/env bash
# -----------------------------
# Assessor-CLI Bash wrapper
# Adds -json, then uploads the
# newest reports/*.json file.
# -----------------------------
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 1. Find the .sh file to run
if [[ $# -gt 0 && -f "$1" && "$1" == *.sh ]]; then # user supplied a path
  assessor_cli="$1"
  shift
else # default: sibling file ?
  assessor_cli="$script_dir/Assessor-CLI.sh"
fi
[[ -x "$assessor_cli" ]] || {
  printf "CLI not found or not executable: %s\n" "$assessor_cli" >&2; exit 1; }

# 2. load env vars from .wrapper.env
env_file="$script_dir/.wrapper.env"
[[ -f "$env_file" ]] || { echo "$env_file missing" >&2; exit 1; }
# shellcheck disable=SC1090
source "$env_file" # load envs
: "${POST_URL:?POST_URL missing in env file}"
: "${POST_BEARER:?POST_BEARER missing in env file}"

# snapshot last report
report_dir="$(dirname "$assessor_cli")/reports"
pre_latest_file=$(ls -1t "$report_dir"/*.json 2>/dev/null | head -n1 || true)

# make sure to remove any \r as this file may have been saved on a windows system; from experience
POST_URL=${POST_URL//$'\r'/}
POST_BEARER=${POST_BEARER//$'\r'/}

# 3. run the CLI with -json added
"$assessor_cli" -json "$@"

# 4. pick newest JSON report
report_dir="$(dirname "$assessor_cli")/reports"
latest_file=$(ls -1t "$report_dir"/*.json 2>/dev/null | head -n1 || true)
[[ -n "$latest_file" ]] || { echo "No JSON reports in $report_dir" >&2; exit 1; }

if [[ -n "$pre_latest_file" && "$latest_file" == "$pre_latest_file" ]]; then
  echo "No new JSON report generated. Aborting upload." >&2
  exit 1
fi

# 5. upload via curl
upload_with_curl() {
  curl -sfSL -X POST \
       -H "Authorization: Bearer ${POST_BEARER}" \
       -F "file=@${latest_file}" \
       "${POST_URL}"
}

if command -v curl >/dev/null 2>&1; then
  upload_with_curl
else
  echo "Curl is not available for uploading" >&2
  exit 1
fi
