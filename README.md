# EPP_UE_BuildTool
A simple Python tool to build an Unreal game and auto-update the project version number.

@author Connor McCloskey, Evil Pear Productions

Made with Python 3.12

This assumes a Windows system, but could be easily updated for Linux/Mac as well.


## About
An easy-to-use script aimed at auto-updating an Unreal `DefaultGame.ini` version number field and then generating a build of the specified UE project.

We're also open sourcing this script - this is a simple operation that should probably be better integrated into the base engine, so barring engine feature updates to enable that, we've provided *some sort* of option and knowledge repo for doing so.

To use the ini file's ProjectVersion field from C++ or Blueprints, refer to the simple C++ code described here: https://forums.unrealengine.com/t/how-to-get-project-version/487787

There are a few variables you need to set to use this tool properly. See either the "Per Project" section in the Python file or use the built-in `helpme` command line argument to see a list of the additional arguments to do so and the settings they change.

This is a great source for additional Unreal Automation Tool info: https://github.com/botman99/ue4-unreal-automation-tool


## Build Naming Convention
Evil Pear Productions uses a standardized versioning name convention:

`date_buildconfig_num`

E.g. `042625_dev_001` indicates the build was on 04.26.25, on Development, first build of the day.

This is then used to make our build directory.

Should your team wish to use a different naming convention, you will need to change the contents of the function `update_version` in the main Python file.


## EPP Build Tool commands
* `helpme` - Prints this info. Congrats, you did it!
* `updatesettingsonly` - Don't run the build, just update the settings and save out to JSON. If not used, the tool will try to run the build process. Does not take in any additional info, and will override anything passed into a "savesettings" argument
* `savesettings` - If true, will save out the inputted settings to JSON, which will be read in as the new defaults in the future. Defaults to false.
* `updategame` - Flag if we should update the UE DefaultGame ini file's project version. True by default.
* `buildconfig` - Set the build config of the Unreal project (Development, DebugGame, or Shipping)
* `enginepath` - Set the path to your Unreal Engine install
* `projectname` - Set the game project name (name of your .uproject file)
* `projectpath` - Set the game's project path (path where your .uproject file exists)
* `buildpath` - Set path of where to archive the packaged game (path where the build goes!)
* `platform` - Set the platform to build for (by default set to Win64)
* `cookcommand` - Specify the cook command to use (by default uses BuildCookRun)

## Examples
* `python epp_build.py helpme` - Display helpme info
* `python epp_build.py platform Linux` - Run a build, targeting Linux
* `python epp_build.py savesettings true cookcommand BuildCookRun projectpath "D:\My Game Projects\Example Project"` - Run a build, saving the inputted settings for the future
