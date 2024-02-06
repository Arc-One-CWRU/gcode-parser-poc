import subprocess
import re

# Using commits for now since they are granular
# In the future, could tag each arcgcode version with its release
# and ditch this variable nonsense
ARCGCODE_VERSION = "f27d9215bc4cc73c5ea0a9288a2751327733b167"


def get_current_arcgcode_version() -> str:
    """Gets the most recent commit on the current branch and returns the hash.
    """
    get_git_commit_cmd = "git rev-parse HEAD"
    result = subprocess.check_output(get_git_commit_cmd, shell=True,
                                     stderr=subprocess.STDOUT,
                                     text=True)
    return result.strip()


def replace_arcgcode_version(version_file_contents: str,
                             new_version: str) -> str:
    pattern = r'(ARCGCODE_VERSION\s*=\s*")[^"]+(")'
    # Don't f-string the whole variable because it will break the regex
    # replacing (The regex will replace new_version with raw hash when running
    # install.py)
    new_version_variable = "ARCGCODE_VERSION" + f' = "{new_version}"'
    file_with_new_ver = re.sub(pattern, new_version_variable,
                               version_file_contents)
    return file_with_new_ver
