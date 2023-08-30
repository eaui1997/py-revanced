#!/bin/bash

dl_gh() {
    for repo in revanced-patches revanced-cli revanced-integrations ; do
    asset_urls=$(wget -qO- "https://api.github.com/repos/revanced/$repo/releases/latest" | jq -r '.assets[] | "\(.browser_download_url) \(.name)"')
        while read -r url names
        do
            echo "Downloading $names from $url"
            wget -q -O "$names" "$url"
        done <<< "$asset_urls"
    done
    echo "All assets downloaded"
}

# Function download YouTube apk from APKmirror
req() {
    wget -q -O "$2" --header="User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:111.0) Gecko/20100101 Firefox/111." "$1"
}

dl_yt() {
    rm -rf $2
    echo "Downloading YouTube $1"
    url="https://www.apkmirror.com/apk/google-inc/youtube/youtube-${1//./-}-release/"
    url="$url$(req "$url" - | grep Variant -A50 | grep ">APK<" -A2 | grep android-apk-download | sed "s#.*-release/##g;s#/\#.*##g")"
    url="https://www.apkmirror.com$(req "$url" - | grep "downloadButton" | sed -n 's;.*href="\(.*key=[^"]*\)">.*;\1;p')"
    url="https://www.apkmirror.com$(req "$url" - | grep "please click" | sed -n 's#.*href="\(.*key=[^"]*\)">.*#\1#;s#amp;##p')&forcebaseapk=true"
    echo "URL: $url"
    req "$url" "$2"
    if [ ! -f $2 ]; then echo failed && exit 1; fi
}

#!/bin/bash

dl_gh() {
    for repo in revanced-patches revanced-cli revanced-integrations ; do
    asset_urls=$(wget -qO- "https://api.github.com/repos/revanced/$repo/releases/latest" | jq -r '.assets[] | "\(.browser_download_url) \(.name)"')
        while read -r url names
        do
            echo "Downloading $names from $url"
            wget -q -O "$names" "$url"
        done <<< "$asset_urls"
    done
    echo "All assets downloaded"
}

# Function download YouTube apk from APKmirror
req() {
    wget -q -O "$2" --header="User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:111.0) Gecko/20100101 Firefox/111." "$1"
}

dl_yt() {
    rm -rf $2
    echo "Downloading YouTube $1"
    url="https://www.apkmirror.com/apk/google-inc/youtube/youtube-${1//./-}-release/"
    url="$url$(req "$url" - | grep Variant -A50 | grep ">APK<" -A2 | grep android-apk-download | sed "s#.*-release/##g;s#/\#.*##g")"
    url="https://www.apkmirror.com$(req "$url" - | grep "downloadButton" | sed -n 's;.*href="\(.*key=[^"]*\)">.*;\1;p')"
    url="https://www.apkmirror.com$(req "$url" - | grep "please click" | sed -n 's#.*href="\(.*key=[^"]*\)">.*#\1#;s#amp;##p')&forcebaseapk=true"
    echo "URL: $url"
    req "$url" "$2"
    if [ ! -f $2 ]; then echo failed && exit 1; fi
}

get_version() {
    version=$(jq -r '.[].compatiblePackages[] | select(.name == "com.google.android.youtube") 
    | .versions[] ' patches.json | sort -r | head -n 1)
}

# Function Patch APK
patch_ytrv() {
echo "Patching YouTube..."
java -jar revanced-cli*.jar patch \
     -m revanced-integrations*.apk \
     -b revanced-patches*.jar \
     youtube-v$version.apk \
     --keystore=ks.keystore \
     -o youtube-revanced-v$version.apk
}

# Function Patch APK
patch_ytrv() {
echo "Patching YouTube..."
java -jar revanced-cli*.jar patch \
     -m revanced-integrations*.apk \
     -b revanced-patches*.jar \
     youtube-v$version.apk \
     --keystore=ks.keystore \
     -o youtube-revanced-v$version.apk
}
