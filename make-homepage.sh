#!/usr/bin/env bash
# Usage: ./make-homepage.sh 3      -> makes designs/3-*.html your index.html (template designs only)
#        ./make-homepage.sh store  -> rebuilds the 1 Exam Prep product site (index.html + all state/level/year folders)
set -e
n="${1:-}"
if [ "$n" = "store" ]; then python3 build.py "${@:2}"; exit 0; fi
f=$(ls designs/${n}-*.html 2>/dev/null | head -n1)
if [ -z "$f" ]; then echo "Pick a design number 1-10 or 'store', e.g. ./make-homepage.sh store"; exit 1; fi
sed 's#\.\./shared/#shared/#g' "$f" > index.html
echo "index.html now uses $f. Commit and push to publish."
