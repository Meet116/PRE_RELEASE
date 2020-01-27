import argparse
import os
import subprocess
from builtins import Exception
import re


def main():
    parser = argparse.ArgumentParser(
        description='Deployment script for applications...')
    parser.add_argument('--pre-release', action='store_true',
                        help='Pre-release for the application')
    parser.add_argument('--default', action='store_true',
                        help='Default state')
    args = parser.parse_args()
    try:
        if args.pre_release :
            release_version=fetch_release_version()
            last_git_tag=check_last_tag(release_version)
            branch_name = os.getenv('BRANCH', 'master')
            cmd = "git checkout {}".format(branch_name)  # To checkout to branchname.
            subprocess.run([cmd], shell=True, check=True)
            release_mesg=generate_release_mesg(last_git_tag)
            check_commit_id(last_git_tag)
            gen_tag(release_version,release_mesg)
    except Exception as e:
        print("Exception occurred during application deployment :{}".format(e))
        raise e


def fetch_release_version() :
    """
    Fetch the release version from the GOCD label
    :return: release version name
    """
    gocd_label = os.environ['GO_PIPELINE_LABEL']
    version = re.findall(r'([0-9]+.[0-9]+.[0-9]+).', gocd_label)  # To fetch the verison from gocd label.
    if not version:
        raise Exception('Could not fetch semantic version from the GoCD label. Please check the Release Label used during build.')
    if not version[0] :
        raise Exception('Could not fetch the version number from the GoCD label . Please check...')
    return "release-{}".format(version[0])

def check_last_tag(release_version):
    """
    Checks the last release tag name with the current version name if both were same then it throws exception.
    :param: release_version version to be released
    :return: last released tag
    """
    cmd=" git ls-remote --tags origin | tail -1 | sed 's:.*/::' | egrep -o 'release-[0-9]+.[0-9]+.[0-9]+'"
    last_tag=commands_output(cmd)
    if last_tag == release_version :
        # delete_tag_cmd = "git push --delete origin {}".format(release_version)
        # subprocess.run([delete_tag_cmd], shell=True, check=True)
        # check_last_tag(release_version)
        raise Exception("Tag name already initialize please check")
    return last_tag

def generate_release_mesg(last_git_tag):
    """
    Generates the release mesg to be push with the tags.
    :param last_git_tag: last release version name to get the MR mesg
    :return: mesg to be pushed with the tags
    """
    feature_release_cmd='git log --pretty="%h - %s (%an)" {}..HEAD | grep "Merge pull request" | grep -E -o "(bug).*$" | grep -E -o "(WEB).* " | uniq'.format(last_git_tag) #To fetch the feature release mesg
    feature_release_note=commands_output(feature_release_cmd)
    bug_release_cmd='git log --pretty="%h - %s (%an)" {}..HEAD | grep "Merge pull request" | grep -E -o "(bug).*$" | grep -E -o "(WEB).* " | uniq'.format(last_git_tag) #To fetch the bug release mesg
    bug_release_note=commands_output(bug_release_cmd)
    if not bug_release_note:
        return "Feature release:- \n{}".format(feature_release_note)
    elif not feature_release_note:
        return "Defects fixed:- \n{}".format(bug_release_note)
    elif not bug_release_note and not feature_release_note:
        return ('Empty release notes')
    else:
        return "Feature release:- \n{} \nDefects fixed:- \n{}".format(feature_release_note,bug_release_note)

def check_commit_id(last_git_tag):
    """
    To check the commit IDs of master develop and last released tags
    :param last_git_tag: Last releaed tag name
    """
    master_commit_ID_cmd = "git rev-parse origin/master"  # To get the master commit ID
    master_commit_ID = commands_output(master_commit_ID_cmd)
    last_tag_commit_ID_cmd = "git rev-list -n 1 {}".format(last_git_tag)  # To get the last tag commit ID
    last_tag_commit_ID = commands_output(last_tag_commit_ID_cmd)
    develop_commit_ID_cmd = "git rev-parse origin/develop"  # To get the develop commit ID.
    develop_commit_ID = commands_output(develop_commit_ID_cmd)
    print(master_commit_ID , last_tag_commit_ID, develop_commit_ID)
    if not develop_commit_ID or not last_tag_commit_ID or not master_commit_ID:  # Null check for variables
        raise Exception('Commit id not found')
    if master_commit_ID == last_tag_commit_ID or develop_commit_ID != master_commit_ID:  # Check the commit id
        raise Exception('No changes detected as compared to latest release. Please check for any pending MR to master and try again.')

def gen_tag(release_version,release_mesg):
    """
    To create and release the tag to the github
    :param release_version: lastest release verison name
    :param release_mesg: Mesg to be pushed with relese tag
    """
    create_tag_cmd="git tag {} -m '{}' ".format(release_version, release_mesg)
    subprocess.run([create_tag_cmd], shell=True, check=True)
    push_tag_cmd="git push origin {} ".format(release_version)
    subprocess.run([push_tag_cmd], shell=True, check=True)

#To store the output of the commands in variables
def commands_output(cmd):
    """
    To store the output of the commands in variables.
    :param cmd: commands that need to be run
    :return: output of the commands
    """
    output=subprocess.check_output([cmd], shell=True).decode('ascii').strip()
    if not output:
        raise Exception('Empty mesg please check...')
    return output

if __name__ == "__main__":
    main()