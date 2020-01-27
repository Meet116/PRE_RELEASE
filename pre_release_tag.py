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
            checkout_master_branch()
            release_mesg=generate_release_mesg(last_git_tag)
            check_commit_id(last_git_tag)
            gen_tag(release_version,release_mesg)
    except Exception as e:
        print("Exception occurred during application deployment :{}".format(e))
        raise e

#To configure the github author name and email.
def fetch_release_version() :
    gocd_label = os.environ['GO_PIPELINE_LABEL']
    version = re.findall(r'([0-9]+.[0-9]+.[0-9]+).', gocd_label)  # To fetch the verison from gocd label.
    if not version:
        raise Exception('Version did not fetch from gocd label please check')
    return "release-{}".format(version[0])

#Compare the last tag with the current tag id both have same name then it delete the the old one.
def check_last_tag(release_version):
    cmd="git ls-remote --tags origin  | tail -1 | cut -d'/' -f3 | cut -d'^' -f1"
    last_tag=commands_output(cmd)
    if last_tag == release_version :
        delete_tag_cmd="git push --delete origin {}".format(release_version)
        commands_to_run(delete_tag_cmd)
        check_last_tag(release_version)
    return last_tag

#To checkout to the master branch.
def checkout_master_branch():
    cmd = "git checkout master" #To checkout to master and pull the updates for the github.
    commands_to_run(cmd)

#To generate the release note message
def generate_release_mesg(last_git_tag):
    feature_release_cmd='git log --pretty="%h - %s (%an)" {}..HEAD | grep "Merge pull request" | grep -E -o "(feature).*$" | cut -d"/" -f2 | cut -d"(" -f1 | sed "s/-/:/2" | uniq'.format(last_git_tag) #To fetch the feature release mesg
    feature_release_note=commands_output(feature_release_cmd)
    bug_release_cmd='git log --pretty="%h - %s (%an)" {}..HEAD | grep "Merge pull request" | grep -E -o "(bug).*$" | cut -d"/" -f2 | cut -d"(" -f1 | sed "s/-/:/2" | uniq'.format(last_git_tag) #To fetch the bug release mesg
    bug_release_note=commands_output(bug_release_cmd)
    if not bug_release_note:
        return "Feature release:- \n{}".format(feature_release_note)
    elif not feature_release_note:
        return "Defects fixed:- \n{}".format(bug_release_note)
    elif not bug_release_note and feature_release_note:
        raise Exception('No new merges to the master branch . Master and last release version were same. ')
    else:
        return "Feature release:- \n{} \nDefects fixed:- \n{}".format(feature_release_note,bug_release_note)

#To check the commit id
def check_commit_id(last_git_tag):
    master_commit_ID_cmd = "git rev-parse origin/master"  # To get the master commit ID
    master_commit_ID = commands_output(master_commit_ID_cmd)
    last_tag_commit_ID_cmd = "git rev-list -n 1 {}".format(last_git_tag)  # To get the last tag commit ID
    last_tag_commit_ID = commands_output(last_tag_commit_ID_cmd)
    develop_commit_ID_cmd = "git rev-parse origin/master"  # To get the develop commit ID.
    develop_commit_ID = commands_output(develop_commit_ID_cmd)
    print("test1")
    print(master_commit_ID , last_tag_commit_ID, develop_commit_ID)
    if not develop_commit_ID or not last_tag_commit_ID or not master_commit_ID:  # Null check for variables
        raise Exception('Commit id not found')
    if master_commit_ID == last_tag_commit_ID or develop_commit_ID != master_commit_ID:  # Check the commit id
        print("test2")
        raise Exception('Commit id for master branch and last release tag is same  or else commit id of master branch and develop branch is not same .')

#To create the tag and push to the remote origin
def gen_tag(release_version,release_mesg):
    create_tag_cmd="git tag {} -m '{}' ".format(release_version, release_mesg)
    commands_to_run(create_tag_cmd)
    push_tag_cmd="git push origin {} ".format(release_version)
    commands_to_run(push_tag_cmd)

#To store the output of the commands in variables
def commands_output(cmd):
    output=subprocess.check_output([cmd], shell=True).decode('ascii').strip()
    return output

#Executes the commands
def commands_to_run(cmd):
    subprocess.run([cmd], shell=True, check=True)


if __name__ == "__main__":
    main()