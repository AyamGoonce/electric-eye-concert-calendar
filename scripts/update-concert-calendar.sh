#!/bin/zsh
set -eu

repository="${ELECTRIC_EYE_CALENDAR_REPOSITORY:-AyamGoonce/electric-eye-concert-calendar}"
branch="${ELECTRIC_EYE_CALENDAR_BRANCH:-supersonic-scraper}"
workflow="Update Electric Eye Concert Calendar"

if ! command -v gh >/dev/null 2>&1; then
  print -u2 "GitHub CLI (gh) is not available. Install it and authenticate with gh auth login."
  exit 1
fi

if ! gh auth status --hostname github.com >/dev/null 2>&1; then
  print -u2 "GitHub authentication is unavailable. Run: gh auth login"
  exit 1
fi

gh workflow run "$workflow" --repo "$repository" --ref "$branch"
print "Calendar update started on GitHub."
print "Status: https://github.com/$repository/actions/workflows/update-calendar.yml"
