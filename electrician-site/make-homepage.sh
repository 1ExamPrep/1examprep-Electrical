#!/usr/bin/env bash
# Usage: ./make-homepage.sh 3      -> makes designs/3-*.html your index.html
#        ./make-homepage.sh store  -> makes the live 1 Exam Prep product page your index.html
set -e
n="${1:-}"
if [ "$n" = "store" ]; then f="store/index.html"; else f=$(ls designs/${n}-*.html 2>/dev/null | head -n1); fi
if [ -z "$f" ] || [ ! -f "$f" ]; then echo "Pick a design number 1-10 or 'store', e.g. ./make-homepage.sh store"; exit 1; fi
sed 's#\.\./shared/#shared/#g' "$f" > index.html
echo "index.html now uses $f. Commit and push to publish."
