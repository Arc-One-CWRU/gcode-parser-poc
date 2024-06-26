import argparse
import os
import shutil
import platform
from arcgcode.processor.base import version


def main(cura_scripts_dir: str):
    """Installs the scripts in the scripts directory.
    """
    print(f"Scripts Directory: {cura_scripts_dir}")
    custom_plugins_dir = os.path.abspath("./plugins")
    package_src_dir = os.path.abspath("./src")
    print(f"Inferred Plugins Dir: {custom_plugins_dir}")
    print(f"Inferred Package Src Dir: {package_src_dir}\n")

    # Try to write in the current version to version.py to make sure that it's
    # always up-to-date
    version_file = os.path.join(package_src_dir, "arcgcode", "processor",
                                "base", "version.py")
    if not os.path.isfile(version_file):
        raise Exception(f"Could not find version file {version_file}. " +
                        "Please contact the software team!")

    curr_version = version.get_current_arcgcode_version()
    if curr_version != version.ARCGCODE_VERSION:
        print(f"Version: {curr_version}")
        # Manually overwrite the ARCGCODE_VERSION in the file
        # Yes, this is hacky, but it works LOL
        with open(version_file, "r+") as f:
            version_py_contents = f.read()
            # Seek and truncate are needed to reset and properly overwrite the
            # file
            # https://stackoverflow.com/questions/11469228/replace-and-overwrite-instead-of-appending
            f.seek(0)
            with_new_version = version.replace_arcgcode_version(version_py_contents,
                                                                new_version=curr_version)
            f.write(with_new_version)
            f.truncate()

    # Cura is not able to import the symlinked library.
    # Must remove the src directory, then copy everything in it to the scripts
    # directory.
    cura_src_path = os.path.join(cura_scripts_dir, "src")
    if os.path.isdir(cura_src_path):
        print(f"Cleaning up Cura src directory {cura_src_path} before " +
              "copying fresh version...")
        shutil.rmtree(cura_src_path)

    try:
        print(f"Copying fresh {package_src_dir} to Cura scripts src dir " +
              f"{cura_src_path}")
        shutil.copytree(package_src_dir, cura_src_path, dirs_exist_ok=True)
    except Exception as e:
        err_msg = str(e)
        okay_linux_err_msg = "[Errno 17] File exists:"
        okay_windows_err_msg = "[WinError 183]"
        is_okay_linux_err = okay_linux_err_msg in err_msg
        is_okay_windows_err = okay_windows_err_msg in err_msg
        if (platform.system() == "Linux" and not is_okay_linux_err) or \
           (platform.system() == "Windows" and not is_okay_windows_err):
            print("Please contact the software team!")
            print("Unexpected error: ", e)
            return
    print(f"Created arcgcode src dir in Cura scripts: {cura_src_path}\n")

    print("Moving Arc Post-Processing Scripts to the correct directory...")
    # Get a list of all files in the source directory
    files = os.listdir(custom_plugins_dir)
    print(f"All files in directory: {files}")  # Print all files in the directory
    # Iterate through all 'plugins' and copy them into the Cura scripts
    # directory.
    for file in files:
        if not file.endswith(".py"):
            continue
        # Create the full file paths for source and target
        source_file_path = os.path.join(custom_plugins_dir, file)
        target_file_path = os.path.join(cura_scripts_dir, file)
        
        # Check if the file is a regular file (not a directory) before
        # creating a symbolic link
        if os.path.isfile(source_file_path):
            shutil.copyfile(source_file_path, target_file_path)
            print(f"Copied {source_file_path} to " +
                  f"{target_file_path}")

    print("You have successfully installed the Cura post-processing scripts!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arc Installation CLI")
    help_descrip = """Path to the Cura scripts directory. In Linux, this may be
    in ~/.local/share/cura/5.3/scripts. To find it, open Cura > Help >
    Show Configuration Folder, then open the scripts directory and that's your
    path!
    """
    parser.add_argument("scripts_dir", type=str,
                        help=help_descrip)

    args = parser.parse_args()
    scripts_dir = args.scripts_dir
    main(scripts_dir)
