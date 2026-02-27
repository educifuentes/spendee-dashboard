BASE_VERSION="v$(date +%y.%m.%d)"
if [ -n "$(git tag -l "$BASE_VERSION")" ]; then
    suffix=1
    while [ -n "$(git tag -l "${BASE_VERSION}.${suffix}")" ]; then
        ((suffix++))
    done
    VERSION="${BASE_VERSION}.${suffix}"
else
    VERSION="$BASE_VERSION"
fi
echo "$VERSION"
