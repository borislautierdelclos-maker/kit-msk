#!/bin/bash
cd "$HOME/Sites/kit-msk" 2>/dev/null || exit 0
if [ -n "$(git status --porcelain)" ]; then
  git add -A
  git commit -m "auto: maj $(date '+%F %T')" >/dev/null 2>&1
  git push >/dev/null 2>&1
fi
