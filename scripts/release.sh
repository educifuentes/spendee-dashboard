#!/bin/bash
set -e

# Generate today's date in calver format YY.MM.DD
BASE_VERSION="v$(date +%y.%m.%d)"

# Check if the base tag already exists
if [ -n "$(git tag -l "$BASE_VERSION")" ]; then
    # Base tag exists, find the next available suffix
    suffix=1
    while [ -n "$(git tag -l "${BASE_VERSION}.${suffix}")" ]; do
        ((suffix++))
    done
    VERSION="${BASE_VERSION}.${suffix}"
else
    VERSION="$BASE_VERSION"
fi

echo "Creating tag $VERSION..."
git tag $VERSION

echo "Pushing tag $VERSION to origin..."
git push origin $VERSION

echo "Release $VERSION initiated successfully!"
