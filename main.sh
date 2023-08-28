#!/bin/bash
source utils.sh

repo1="$GITHUB_REPOSITORY"
repo2="revanced/revanced-patches"
time_threshold=24

current_time=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Check the release status of repo1
response1=$(curl -s -o /dev/null -w "%{http_code}" "https://api.github.com/repos/$repo1/releases/latest")
if [[ $response1 -eq 404 ]]; then
    # No latest release, build the app
    dl_gh
    get_version
    dl_yt $version youtube-v$version.apk
    patch_ytrv
else
    # There is a latest release, check the release status of repo2
    response2=$(curl -s -o /dev/null -w "%{http_code}" "https://api.github.com/repos/$repo2/releases/latest")
    if [[ $response2 -eq 200 ]]; then
        # There is a latest release, get the published time of the assets
        assets=$(curl -s "https://api.github.com/repos/$repo2/releases/latest" | jq -r '.assets')

        if [[ $assets ]]; then
            # There are assets, get the first one
            asset=$(echo "$assets" | jq -r '.[0]')
            published_at=$(echo "$asset" | jq -r '.updated_at')

            # Convert the published time to datetime object
            published_time=$(date -u -d "$published_at" +"%Y-%m-%dT%H:%M:%SZ")

            # Calculate the difference in hours
            difference=$(( ($(date -u -d "$current_time" +"%s") - $(date -u -d "$published_time" +"%s")) / 3600 ))

            if [[ $difference -le $time_threshold ]]; then
                # The asset is published within the time threshold, build the app
                dl_gh
                get_version
                dl_yt $version youtube-v$version.apk
                patch_ytrv
            else
                # The asset is too old, skip the app
                echo "Skipping patch YouTube because the asset of $repo2 is older than $time_threshold hour(s)"
            fi
        else
            # There are no assets, skip the app
            echo "Skipping patch YouTube because there are no assets in $repo2"
        fi
    else
        # There is no latest release, skip the app
        echo "Skipping patch YouTube because there is no available latest release in $repo1"
    fi
fi
