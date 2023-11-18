import subprocess
import re

# Using commits for now since they are granular
# In the future, could tag each arcgcode version with its release
# and ditch this variable nonsense
ARCGCODE_VERSION = "3b391a7a6ecbcc1fe6a19ee4e4cb3320b7f5b705"


def get_current_arcgcode_version() -> str:
    """Gets the most recent commit on the current branch and returns the hash.
    """
    get_git_commit_cmd = "git rev-parse HEAD"
    result = subprocess.check_output(get_git_commit_cmd, shell=True,  stderr=subprocess.STDOUT,
                                     text=True)
    return result.strip()


def replace_arcgcode_version(version_file_contents: str, new_version: str) -> str:
    pattern = r'(ARCGCODE_VERSION\s*=\s*")[^"]+(")'
    new_version_variable = f'ARCGCODE_VERSION = "{new_version}"'
    file_with_new_ver = re.sub(pattern, new_version_variable, version_file_contents)
    return file_with_new_ver
