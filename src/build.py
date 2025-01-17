import os
import subprocess
import sys
from loguru import logger
from src._config import config
from src.downloader import Downloader

class Build(object):
    def __init__(self, args):
        if not os.path.exists(config["dist_dir"]):
            os.mkdir(config["dist_dir"])
        
        self.args = args
        self.check_java_version()
        self.download_files = Downloader().download_required()
        self.exclude_patches: str | None = self.args.exclude_patches
        self.include_patches: str | None = self.args.include_patches

    def run_build(self):
        target_app = self.args.app_name.lower().strip()
        input_apk_filepath = Downloader().download_apk(target_app)
    
        logger.info(f"Running build for {target_app}:")
     
        exclude_patches = sum(
            [["--exclude", s.strip()] for s in self.args.exclude_patches.split(",")],
            [],
        )
    
        include_patches = sum(
            [["--include", s.strip()] for s in self.args.include_patches.split(",")],
            [],
        )
    
        process = subprocess.Popen(
            [
                "java",
                "-jar",
                self.download_files["revanced-cli"],
                "patch",
                "-b",
                self.download_files["revanced-patches"],
                "-o",
                f"{target_app}-revanced.apk",
                "-m",
                self.download_files["revanced-integrations"],
                "--keystore",
                config["keystore_path"],
                *exclude_patches,
                *include_patches,
                 input_apk_filepath,
            ],
            stdout=subprocess.PIPE,
        )
    
        output = process.stdout
    
        for line in output:
            print(line.decode("utf-8"), end="")
    
        if process.wait() != 0:
            logger.error("An error occurred while running the Java program")
            sys.exit(1)
    
        logger.success(f"Build completed successfully")

    def check_java_version(self):
        version = subprocess.check_output(
            ["java", "-version"], stderr=subprocess.STDOUT
        ).decode("utf-8")
        
        if "17" not in version:
            logger.error("Java 17 is required to run the build.")
            exit(1)
        
        logger.success("Java 17 is installed")
