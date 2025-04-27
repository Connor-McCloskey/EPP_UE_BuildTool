"""
A simple Python tool to build an Unreal game
@author Connor McCloskey

Made with Python 3.12
This assumes a Windows system, but could be easily configured for a Unix-styled terminal too

There are a few paths in the Config Vars section you need to set for your machine -> See "TODO" comment!

We're also open-sourcing this script, because I hate that there's no easy info on this out there...

We are combining this with updating the game version in the ini files automatically
This can be retrieved in UE with the simple C++ code described here:
https://forums.unrealengine.com/t/how-to-get-project-version/487787

This is a great source of UAT info:
https://github.com/botman99/ue4-unreal-automation-tool

### Changelog ###
4.27.25
- Added various command line args for easier use
- Updated fields to make it *very clear* what vars a user should update
- Add some abilities to save out project-specific stuff to a settings JSON
- Adding some type hinting, because I prefer static typing where possible...so getting there with what Python will allow!
- Ensured set cook command is used by the build commands array
- Moving stuff around so it could theoretically be started by another script...
"""

#region --- Imports ---

import os
import subprocess
import sys
import configparser
import json
from datetime import datetime

#endregion

#region --- Vars ---

#region - Per Project -

""" TODO - Change these for your project! Can also be set via command line args """

project_name:       str = "MyGame"                                      # Uproject file name
project_path:       str = "D:\\MyGameProjects\\MyGame"                  # Path to the project file
build_config:       str = "Development"                                 # DebugGame, Development, Shipping # Desired build config
platform:           str = "Win64"                                       # Desired platform
builds_dir:         str = "D:\\MyGameProjects\\Builds\\MyGameBuilds\\"  # Directory where you wish builds to be archived at
cook_command:       str = "BuildCookRun"                                # Specific cook command

uat_path:           str = "C:\\Program Files\\Epic Games\\UE_5.4\\Engine\\Build\\BatchFiles\\RunUAT.bat" # Path to your Unreal Engine installation's RunUAT batch file
#endregion

#region - Generated -

new_version:        str = ""    # New version name
archive_dir:        str = ""    # Generated directory where the packaged project should be placed

#endregion

#region - Constants -

version_section:    str = "/Script/EngineSettings.GeneralProjectSettings"   # Game version section in UE DefaultGame config file
build_config_name:  dict = {
    "Development":  "dev",
    "DebugGame":    "debug",
    "Shipping":     "shipping"
}
settings_file_name: str = "settings.json"

#endregion

#endregion

#region --- Functions ---

#region - Set script global vars -
def set_new_version(v: str):
    global new_version
    new_version = v

def set_project_path(path: str):
    global project_path
    project_path = path

def set_project_name(name: str):
    global project_name
    project_name = name

def set_uat_path(path: str):
    global uat_path
    uat_path = path

def set_build_path(path: str):
    global builds_dir
    builds_dir = path

def set_build_config(build_type: str):
    global build_config
    build_config = build_type

def set_cook_command(cmd: str):
    global cook_command
    cook_command = cmd

def set_platform(p: str):
    global platform
    platform = p
#endregion

def make_archive_directory():
    global archive_dir

    new_directory = os.path.join(builds_dir, new_version)
    os.mkdir(new_directory)

    archive_dir = new_directory

def save_config(config, config_path):
    with open(config_path, 'w') as configfile:
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

    config = configparser.ConfigParser(strict=False)
    config_file_path = os.path.join(project_path, "Config\\DefaultGame.ini")
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

    save_config(config, config_file_path)
    set_new_version(version)

def read_settings_json():

    if not os.path.exists(settings_file_name):
        print(">>>>> No settings file found. Using script defaults.")
        return

    file = open(settings_file_name, "r")
    settings = json.load(file)
    file.close()

    set_project_path(settings["projectpath"])
    set_project_name(settings["projectname"])
    set_uat_path(settings["uatpath"])
    set_build_path(settings["buildpath"])
    set_build_config(settings["buildconfig"])
    set_cook_command(settings["cookcommand"])
    set_platform(settings["platform"])

    print(">>>>> Imported settings from JSON")

def write_settings_json():
    new_settings = {
        "projectpath": project_path,
        "projectname": project_name,
        "uatpath": uat_path,
        "buildpath": builds_dir,
        "buildconfig": build_config,
        "cookcommand": cook_command,
        "platform": platform
    }

    json_data = json.dumps(new_settings)

    file = open(settings_file_name, "w")
    file.write(json_data)
    file.close()

    print(">>>>> Wrote settings to JSON")

def helpme():
    print(    """
    *** EPP Build Tool commands ***
        helpme                  Prints this info. Congrats, you did it!
        
        updatesettingsonly      Don't run the build, just update the settings and save out to JSON. If not specified, will try to run the build process.
                                Does not take in any additional info, and will override anything passed into a "savesettings" argument

        savesettings            If true, will save out the inputted settings to JSON, which will be read in as the new defaults in the future. Defaults to false.
        
        buildconfig             Set the build config (dev, debuggame, shipping)
        uatpath                 Set the user's UAT path
        projectname             Set the game project name
        projectpath             Set the game's project path
        buildpath               Set path of where to archive the packaged game
        platform                Set the platforms to build for
        cookcommand             Specify the cook command to use
    *******************************
    """)

def make_build():

    print(">>>>> UPDATING VERSION IN CONFIG FILE...")
    update_version()

    print(">>>>> CREATING OUTPUT DIRECTORY...")
    make_archive_directory()

    build_command = [
        uat_path,
        cook_command,
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

    print(">>>>> PACKAGING GAME...")
    print("")

    try:
        result = subprocess.run(build_command, shell=True, check=True)
        print("")
        print(">>>>> PACKAGING DONE! Return code: ", result.returncode)
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print("")
        print(">>>>> PACKAGING FAILED: ", e)
        sys.exit(1)

def process_args():

    print(">>>>> Processing command line arguments")

    num_args = len(sys.argv)

    # First, if no args, we assume it's just a standard build with the saved/current settings
    if num_args == 0:
        make_build()
        return

    # Operation flags
    update_settings_only: bool = False
    save_settings: bool = False

    # Go through the array of sys args and sort them into key-value pairs
    # Makes it easier to just take all items in, and then ingest them in our desired order of operations...
    sorted_args: dict = {}
    index = 1
    while index < num_args:
        key = sys.argv[index].lower()
        if key == "helpme":
            helpme()
            sys.exit(0)
        if key == "updatesettingsonly":
            update_settings_only = True
            save_settings = True
            sorted_args[key] = "True" # Do this just to follow the format
            index += 1
            continue
        value = sys.argv[index + 1]
        sorted_args[key] = value
        index += 2

    # Now, go through any settings that were passed in and update them

    # Determine if we should save settings
    if update_settings_only == False and "savesettings" in sorted_args:
        v = sorted_args["savesettings"]
        if v.tolower() == "true":
            save_settings = True

    # Set project name
    if "projectname" in sorted_args:
        v = sorted_args["projectname"]
        set_project_name(v)

    # Set project path
    if "projectpath" in sorted_args:
        v = sorted_args["projectpath"]
        set_project_path(v)

    # Set UAT path
    if "uatpath" in sorted_args:
        v = sorted_args["uatpath"]
        set_uat_path(v)

    # Set build path
    if "buildpath" in sorted_args:
        v = sorted_args["buildpath"]
        set_project_path(v)

    # Set build config
    if "buildconfig" in sorted_args:
        v = sorted_args["buildpath"].lower()
        if v == "dev" or v == "development":
            set_build_config("Development")
        elif v == "debug" or "debuggame":
            set_build_config("DebugGame")
        elif v == "shipping":
            set_build_config("Shipping")
        else:
            set_build_config("Development")

    # Set cook command
    if "cookcommand" in sorted_args:
        v = sorted_args["cookcommand"]
        set_cook_command(v)

    # Set platform
    if "platform" in sorted_args:
        v = sorted_args["platform"]
        set_platform(v)

    # Now, if we were told to only update the settings, return and exit
    # Else, make the build!
    if update_settings_only:
        write_settings_json()
        print(">>>>> Settings update complete. Exiting.")
        sys.exit(0)
    else:
        if save_settings:
            write_settings_json()
        make_build()

def start_tool():

    print(">>>>>>>>>> RUNNING EPP UNREAL BUILD TOOL <<<<<<<<<<")

    read_settings_json()
    process_args()
#endregion

#region --- Main ---

def main():
    start_tool()

#endregion

if __name__ == "__main__":
    main()
