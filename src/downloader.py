import json
import os
import requests

from loguru import logger
from src._config import app_reference, config
from src.apkmirror import APKmirror

class Downloader:
    def __init__(self):
        self.client = requests.Session()
        self.client.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0)"
                + " Gecko/20100101 Firefox/112.0"
            }
        )
        self.base_url = "https://api.github.com/repos"
        self.repositories = [
            {"user": "revanced", "repo": "revanced-cli", "tag": "tags/v2.22.0"},
            {"user": "revanced", "repo": "revanced-patches", "tag": "latest"},
            {"user": "revanced", "repo": "revanced-integrations", "tag": "latest"}
        ]

    def _download(self, url: str, name: str) -> str:
        filepath = f"./{config['dist_dir']}/{name}"

        # Check if the file already exists
        if os.path.exists(filepath):
            logger.warning(f"{filepath} already exists, skipping")
            return filepath

        with self.client.get(url, stream=True) as res:
            res.raise_for_status()
         
            with open(filepath, "wb") as file:
                for chunk in res.iter_content(chunk_size=8192):
                    file.write(chunk)

        logger.success(f"{filepath} downloaded")
        logger.info(f"Download link: {url}")

        return filepath

    def download_required(self):
        logger.info("Downloading required resources")
        downloaded_files = {}

        for repository in self.repositories:
            try:
                api_url = f"{self.base_url}/{repository['user']}/{repository['repo']}/releases/{repository['tag']}"
                response = self.client.get(api_url)
                response.raise_for_status()

                assets = response.json().get("assets", [])

                for asset in assets:
                    filename = asset["name"]
                    download_url = asset["browser_download_url"]
                    filepath = self._download(download_url, filename)
                    name = repository['repo'].replace("user/", "")
                    downloaded_files[name] = filepath

            except requests.exceptions.HTTPError as err:
                logger.error(f"Error downloading resources for {repository['user']}/{repository['repo']}: {err}")
                continue

        return downloaded_files            

    def download_apk(self, app_name: str):
        # Load from patches.json
        with open(f"./{config['dist_dir']}/patches.json", "r") as patches_file:
            patches = json.load(patches_file)

            for patch in patches:
                for package in patch["compatiblePackages"]:
                    if package["name"] == app_reference[app_name]["name"]:
                        version = package["versions"]

                        if len(version) == 0:
                            continue

                        version = version[-1]

                        page = (
                            f"{app_reference[app_name]['apkmirror']}"
                            + f"-{version.replace('.', '-')}-release/"
                        )

                        download_page = APKmirror().get_download_page(url=page)

                        href = APKmirror().extract_download_link(download_page)

                        filename = f"{app_reference[app_name]['name']}-{version}.apk"

                        return self._download(href, filename)
                        
