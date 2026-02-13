#!/bin/bash

# Ensure we're inside a git repo
if [ ! -d .git ]; then
  echo "Not a git repository!"
  exit 1
fi

# Add and commit each file one by one
for file in $(git ls-files -o -m --exclude-standard); do
  git add "$file"
  git commit -m "Add/update $file"
done

echo "✅ All files committed one by one."