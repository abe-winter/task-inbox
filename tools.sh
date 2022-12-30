#!/usr/bin/env bash
# this inventories the executables you need for repo setup and says whether they're present or not
# it doesn't install anything

# note: I think direnv will install pipenv in the virtualenv? If not, add it here.
tools="python3 direnv docker git-bug pipenv"

for tool in $tools; do
  if ! command -v $tool &> /dev/null; then
    echo ❌ $tool
  else
    echo ✅ $tool
  fi
done
