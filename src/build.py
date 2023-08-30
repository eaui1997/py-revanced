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
            f"./{config['dist_dir']}/{target_app}-revanced.apk",
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
    
    # 不验证 output_path
    
    logger.success(f"Build completed successfully")
