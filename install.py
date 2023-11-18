import argparse
import os
import shutil
import platform


def main(cura_scripts_dir: str):
    """Installs the scripts in the scripts directory.
    """
    print(f"Scripts Directory: {cura_scripts_dir}")
    custom_plugins_dir = os.path.abspath("./plugins")
    package_src_dir = os.path.abspath("./src")
    print(f"Inferred Plugins Dir: {custom_plugins_dir}")
    print(f"Inferred Package Src Dir: {package_src_dir}\n")
    src_symlink_path = os.path.join(cura_scripts_dir, "src")

    # TODO: what was I trying to do here lol?
    # if not os.path.isdir(src_symlink_path):
    #     print("inferred src dir is not a directory: {src_symlink_path}")
    #     raise Exception("Please run the install script in the root directory"
    #  +
    #                     " of this repository.")

    try:
        os.symlink(package_src_dir, src_symlink_path)
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

    print(f"Created symlink for arcgcode src dir: {package_src_dir} to " +
          f"{src_symlink_path}\n")

    print("Moving Arc Post-Processing Scripts to the correct directory...")
    # Create a symlink from ./src to the scripts dir
    # Then create a symlink for each plugin to the scripts directory.
    # Get a list of all files in the source directory
    files = os.listdir(custom_plugins_dir)
    # ???? $$$
    # Iterate through the files and create symbolic links in the target
    # directory
    for file in files:
        if not file.endswith(".py"):
            continue
        # Create the full file paths for source and target
        source_file_path = os.path.join(custom_plugins_dir, file)
        target_file_path = os.path.join(cura_scripts_dir, file)
        
        # Check if the file is a regular file (not a directory) before
        # creating a symbolic link
        if os.path.isfile(source_file_path):
            
            # Create a symbolic link in the target directory pointing to the
            # source file
            # os.symlink(source_file_path, target_file_path)
            # print(f"Symbolic link created for {source_file_path} to " +
            #       f"{target_file_path}")
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
