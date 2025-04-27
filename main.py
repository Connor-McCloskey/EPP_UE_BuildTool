"""
A simple Python tool to build an Unreal game
@author Connor McCloskey

Made with Python 3.12
This assumes a Windows system, but could be easily configured for a Unix-styled terminal too

We're also open-sourcing this script, because I hate that there's no easy info on this out there...

We are combining this with updating the game version in the ini files automatically
This can be retrieved in UE with the simple C++ code described here:
https://forums.unrealengine.com/t/how-to-get-project-version/487787

This is a great source of UAT info:
https://github.com/botman99/ue4-unreal-automation-tool

"""

#region --- Imports ---

import os
import subprocess
import sys
import configparser
from datetime import datetime

#endregion

#region --- Config ---

# Uproject file name
project_name = "MyGame"

# Path to the project file
project_path = ""

# Path to the project config file containing the game version (DefaultGame.ini)
config_file_path = ""

# Desired build config
build_config = "Development" # DebugGame, Development, Shipping
build_config_name = {
    "Development": "dev",
    "DebugGame": "debug",
    "Shipping": "shipping"
}

# Desired platform
platform = "Win64"

# Game version section in Config file
version_section = "[/Script/EngineSettings.GeneralProjectSettings]"

# new version
new_version = ""

# Base build directory on your machine
builds_dir = ""

# Directory where the packaged project should be placed
archive_dir = ""

# Path to your Unreal Engine installation's RunUAT batch file
uat_path = ""

# Specific cook command
cook_command = "BuildCookRun"
#endregion

def make_archive_directory():
    global archive_dir

    new_directory = os.path.join(builds_dir, new_version)
    os.mkdir(new_directory)

    archive_dir = new_directory

def set_new_version(v):
    global new_version
    new_version = v

def save_config(config):
    with open(config_file_path, 'w') as configfile:
        config.write(configfile)
    configfile.close()

def update_version():
    # EPP uses a standardized versioning name convention:
    # date_buildconfig_num
    # E.g. 042625_dev_001 indicates the build was on 04.26.25, on Development, first build of the day
    # This is then used to make our build directory

    # Config is stored in the DefaultGame.ini file,
    # section [/Script/EngineSettings.GeneralProjectSettings]
    # as ProjectVersion=042625_dev_001

    # If you/your team use a different standard, feel free to update this as needed!

    build_date = datetime.today().strftime('%m%d%y')

    config = configparser.ConfigParser()
    config.read(config_file_path)
    build = build_config_name[build_config]
    version = ""

    # Check to see if this section exists or not
    # If so, we can grab it and try to update it
    if config.has_option(version_section,"ProjectVersion"):
        # Retrieve the data of the last version built, according to the config file
        last_version = config.get(version_section, "ProjectVersion")

        split = last_version.split("_") # Returns 3 elements
        last_build_date = split[0]

        # If the dates don't match, we just start at '001'
        if last_build_date != build_date:
            version = build_date + "_" + build + "_001"
            config.set(version_section, "ProjectVersion", version)
        # If they do match, we can update it!
        else:
            new_build_int = int(split[2]) + 1
            new_build_formatted = "{:03d}".format(new_build_int)
            version = build_date + "_" + build + "_" + new_build_formatted
            config.set(version_section, "ProjectVersion", version)
    # If not, create it
    else:
        version = build_date + "_" + build + "_001"
        config.set(version_section, "ProjectVersion", version)

    save_config(config)
    set_new_version(version)

def main():

    print("UPDATING VERSION...")
    update_version()

    print("CREATING BUILD DIRECTORY...")
    make_archive_directory()

    # if True:
        # return

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

if __name__ == "__main__":
    main()
