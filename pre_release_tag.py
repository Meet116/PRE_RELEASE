import os
import subprocess
from builtins import Exception
import re


def main():
    try:
        deploy_to = "_" + os.environ['DEPLOY_TO'].upper()
        branch_name= os.environ['BRANCH']
        gocd_label = os.environ['GO_PIPELINE_LABEL']
        if not branch_name:
            raise Exception("Branch name not set in env variable. Please check.")
        if deploy_to in ["_MY", "_MY2"]:
            check_master_merge(branch_name)
            release_version=fetch_release_version(gocd_label)
            last_git_tag=check_last_tag(release_version)
            release_mesg=generate_release_mesg(last_git_tag)
            gen_tag(release_version, release_mesg)
        elif deploy_to == "_STAGING":
            release_branch(gocd_label)
    except Exception as e:
        print("Exception occurred during application deployment :{}".format(e))
        raise e

def release_branch(gocd_label):
    """
    To create the name of the release branch and fetch the version form gocd_label.
    If the branch name already exists in repo it just print the mesg branch  already created.
    :param gocd_label: Gocd label to fetch the version.
    """
    version = re.findall(r'^([0-9]+.[0-9]+).', gocd_label)
    if not version:
        raise Exception("Please check the label .")
    else:
        last_release_branch_cmd = "git ls-remote --heads origin | grep 'release-*' | tail -1 | grep -E -o 'release-[0-9]+.[0-9]+.[0-9]+'"
        last_release_branch = subprocess.check_output([last_release_branch_cmd], shell=True).decode('ascii').strip()
        release_branch = "release-{}.0".format(version[0])
        if last_release_branch == release_branch:
            print("Branch already created")
        else:
            create_release_branch(release_branch)

def create_release_branch(release_branch):
    """
    To checkout and push the release branch to the repository.
    :param release_branch: Release branch name.
    """
    release_branch_cmd = "git checkout -b {}".format(release_branch)
    subprocess.run([release_branch_cmd], shell=True, check=True)
    release_branch_push_cmd = "git push origin {}".format(release_branch)
    subprocess.run([release_branch_push_cmd], shell=True, check=True)

def check_master_merge(branch_name):
    """
    Check the commit id of the release branch and the master branch.
    :param branch_name: Branch name to be merged.
    """
    release_branch_commit_ID_cmd = 'git rev-parse origin/{}'.format(branch_name)
    release_branch_commit_Id=subprocess.check_output([release_branch_commit_ID_cmd], shell=True).decode('ascii').strip()
    release_branch_commit_Id = release_branch_commit_Id[:7]
    if not release_branch_commit_Id:
        raise Exception("Empty last release branch commit ID. Please check")
    checkout_master_cmd="git checkout master"
    subprocess.run([checkout_master_cmd], shell=True, check=True)
    check_master_cmd ="git log -r master | grep Merge | head -1 |  awk '{print $3}'"
    check_master=subprocess.check_output([check_master_cmd], shell=True ).decode('ascii').strip()
    if check_master != release_branch_commit_Id:
        raise Exception("Please merge the latest updates to master branch")


def fetch_release_version(gocd_label) :
    """
    Fetch the release version from the GOCD label
    :return: release version name
    """
    version = re.findall(r'^([0-9]+.[0-9]+.[0-9]+).', gocd_label)  # To fetch the verison from gocd label.
    if not version:
        raise Exception('Could not fetch semantic version from the GoCD label. Please check the Release Label used during build.')
    if not version[0] :
        raise Exception('Could not fetch the version number from the GoCD label . Please check...')
    return version[0]

def check_last_tag(release_version):
    """
    Checks the last release tag name with the current version name if both were same then it throws exception.
    :param: release_version version to be released
    :return: last released tag
    """
    cmd="git for-each-ref --sort=taggerdate --format '%(refname) %(taggerdate)' refs/tags/[0-9]* | tail -1 | grep -E -o '[0-9]+.[0-9]+.[0-9]+' | head -1"
    last_tag=subprocess.check_output([cmd], shell=True).decode('ascii').strip()
    if not last_tag:
        raise Exception("Last tag not found . Please check")
    return last_tag

def generate_release_mesg(last_git_tag):
    """
    Generates the release mesg to be push with the tags.
    :param last_git_tag: last release version name to get the MR mesg
    :return: mesg to be pushed with the tags
    """

    feature_release_cmd='git log --pretty="%h - %s (%an)" {}..HEAD | grep "Merge pull request" | grep -E -o "(feature).*$" | grep -E -o "(WEB).*" | sed "s/-/:/2" | uniq'.format(last_git_tag) #To fetch the feature release mesg
    feature_release_note=subprocess.check_output([feature_release_cmd], shell=True).decode('ascii').strip()
    bug_release_cmd='git log --pretty="%h - %s (%an)" {}..HEAD | grep "Merge pull request" | grep -E -o "(bug).*$" | grep -E -o "(WEB).*" | sed "s/-/:/2" | uniq'.format(last_git_tag) #To fetch the bug release mesg
    bug_release_note=subprocess.check_output([bug_release_cmd], shell=True).decode('ascii').strip()
    if not bug_release_note and feature_release_note:
        return "Feature release:- \n{}".format(feature_release_note)
    elif not feature_release_note and bug_release_note:
        return "Defects fixed:- \n{}".format(bug_release_note)
    elif not bug_release_note and not feature_release_note:
        return ('Empty release notes')
    else:
        return "Feature release:- \n{} \nDefects fixed:- \n{}".format(feature_release_note,bug_release_note)

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


if __name__ == "__main__":
    main()