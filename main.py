"""
A simple Python tool to build an Unreal game
@author Connor McCloskey

Made with Python 3.12
This assumes a Windows system, but could be easily configured for a Unix-styled terminal too
"""

#region --- Imports ---

import os
import subprocess
import sys

#endregion

#region --- Config ---

# Uproject file name
project_name = "MyGame"

# Path to the project file
project_path = ""

# Desired build config
build_config = "Development" # DebugGame, Development, Shipping

# Desired platform
platform = "Win64"

# Directory where the packaged project should be placed
archive_dir = ""

# Path to your Unreal Engine installation's RunUAT batch file
uat_path = ""

# Specific cook command
cook_command = "BuildCookRun"
#endregion

def make_archive_directory():
    pass

def updated_version():
    pass

def main():
    build_command = [
        uat_path,
        "BuildCookRun",
        f"-project={os.path.join(project_path, f'{project_name}.uproject')}",
        "-noP4",
        f"-platform={platform}",
        f"-clientconfig={build_config}",
        "-cook",
        "-build",
        "-stage",
        "-pak",
        "-archive",
        f"-archivedirectory={archive_dir}"
    ]

    print("PACKAGING GAME...")

    try:
        result = subprocess.run(build_command, shell=True, check=True)
        print("PACKAGING DONE! Return code: ", result.returncode)
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print("Packaging failed: ", e)
        sys.exit(1)

if __name__ == "main":
    main()
