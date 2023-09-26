import argparse
import datetime
import os
import requests

from src.build import Build

app_name = "youtube"
exclude_patches = ""
include_patches = "custom-branding"

# Define the repositories to check
repo1 = os.environ["GITHUB_REPOSITORY"]
repo2 = "revanced/revanced-patches"

# Define the time threshold for assets in hours
time_threshold = 24

args = argparse.Namespace(app_name=app_name, exclude_patches=exclude_patches, include_patches=include_patches)

# Check the release status of repo1
response1 = requests.head(f"https://api.github.com/repos/{repo1}/releases/latest")
if response1.status_code == 404:
    # No latest release, build the app
    build = Build(args)
    build.run_build()
else:
    # There is a latest release, check the release status of repo2
    response2 = requests.get(f"https://api.github.com/repos/{repo2}/releases/latest")
    if response2.status_code == 200:
        # There is a latest release, get the published time of the assets
        data2 = response2.json()
        assets = data2["assets"]
        if assets:
            # There are assets, get the first one
            asset = assets[0]
            published_at = asset["updated_at"]
            # Convert the published time to datetime object
            published_time = datetime.datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
            # Get the current time in UTC
            current_time = datetime.datetime.utcnow()
            # Calculate the difference in hours
            difference = (current_time - published_time).total_seconds() / 3600
            if difference <= time_threshold:
                # The asset is published within the time threshold, build the app
                build = Build(args)
                build.run_build()
            else:
                # The asset is too old, skip the app
                print(f"Skipping patch {app_name} because the asset of {repo2} is older than {time_threshold} hour(s)")
        else:
            # There are no assets, skip the app
            print(f"Skipping patch {app_name} because there are no assets in {repo2}")
    else:
        # There is no latest release, skip the app
        print(f"Skipping patch {app_name} because there is available latest release in {repo1}")
