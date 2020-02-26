import argparse
import os
import subprocess
import sys
import time
import json
import requests
import re


def main():
    parser = argparse.ArgumentParser(description='Deployment script for applications...')
    parser.add_argument('--pre-release', action='store_true', help='pre release stage')
    parser.add_argument('--service-name', action='store', help='service name')
    args = parser.parse_args()

    if args.pre_release:
        print("Pre release for micro-service: {}".format(args.service_name))
    else:
        print("Starting deployment for micro-service: {}".format(args.service_name))
        deploy_stage(args.service_name)


def deploy_stage(service_name):
    """
    Deploy application to specified environment
    :param: service_name : name of the service
    :return: error if any
    """
    try:
        deploy_env = "_" + os.environ['DEPLOY_TO'].upper()
        # Initialize default to False, if not found
        deploy_to_qa = os.getenv('DEPLOY_TO_QA', '').upper() == 'TRUE'
        store_artifact = os.getenv('STORE_RELEASE_ARTIFACTS', '').upper() == 'TRUE'

        version_label = os.getenv('GO_PIPELINE_LABEL', int(time.time()))
        if not deploy_to_qa and deploy_env == '_QA':
            # If requirement for deploying hotfix on staging onwards only
            print("Skipping application deployment to QA environment...")
        else:
            # deploy_application_to_ebs(
            #     os.environ['APP_NAME' + deploy_env],
            #     os.environ['APP_ENV' + deploy_env],
            #     os.path.join(os.getcwd(), service_name + '.zip'),
            #     version_label + '.zip',
            #     version_label,
            #     os.environ['S3_BUCKET_PATH' + deploy_env],
            #     deploy_env,
            #     service_name,
            #     store_artifact
            # )
            deploy_staging_my(deploy_env,version_label)
    except Exception as e:
        print("Exception occurred during application deployment stage:{}".format(e))
        raise e


def deploy_application_to_ebs(app_name, app_env, source_path, destination_jar_name, version_label, s3_bucket, deploy_to, service_name, store_artifact):
    """
    Deploy application zip to elasticbeanstalk
    :param app_name: Application name on elasticbeanstalk
    :param app_env: Environment name on elasticbeanstalk
    :param source_path: Source path for the application zip
    :param destination_jar_name: Name of jar to be uploaded on S3
    :param version_label: Unique application version label
    :param s3_bucket: S3 bucket name
    :param deploy_to: deployment environment
    :param service_name: name of the micro service
    :param store_artifact: whether to store deployed release artifact on S3
    :return: error, if any
    """
    try:
        # Upload application zip to s3 bucket
    #     region = os.environ['AWSREGION' + deploy_to]
    #     access_key = os.environ['AWS_ACCESS_KEY_ID' + deploy_to]
    #     secret_key = os.environ['AWS_SECRET_ACCESS_KEY' + deploy_to]
    #
    #     print("Uploading application ZIP to S3 bucket from {}...".format(os.getcwd()))
    #     cmd_upload_s3 = "AWS_ACCESS_KEY_ID={} AWS_SECRET_ACCESS_KEY={} aws s3 cp {} s3://{}/{} > /dev/null".format(
    #         access_key,
    #         secret_key,
    #         source_path,
    #         s3_bucket,
    #         destination_jar_name
    #     )
    #     subprocess.run([cmd_upload_s3], shell=True, check=True)
    #
    #     if deploy_to in ["_MY", "_MY2"] or store_artifact:
    #         print("Uploading application ZIP to S3 artifact bucket from {}...".format(os.getcwd()))
    #         pipeline_label = os.environ['GO_PIPELINE_LABEL']
    #         rel_version = re.findall(r'([0-9]+.[0-9]+.[0-9]+).', pipeline_label)
    #         if rel_version:
    #             release_version = rel_version[0]
    #             print("release version:{}", release_version)
    #             cmd_upload_s3 = "AWS_ACCESS_KEY_ID={} AWS_SECRET_ACCESS_KEY={} aws s3 cp {} s3://{}/releases/{}/{}/{}/{} > /dev/null".format(
    #                 access_key,
    #                 secret_key,
    #                 source_path,
    #                 os.environ['RELEASE_BUCKET'],
    #                 os.environ['DEPLOY_TO'].lower(),
    #                 release_version,
    #                 service_name,
    #                 destination_jar_name
    #             )
    #             subprocess.run([cmd_upload_s3], shell=True, check=True)
    #
    #     # Check if application version with same name exists on EBS (useful in cases of rerun or hotfixes)
    #     print("Checking if application version with same name exists...")
    #     cmd_app_version = "AWS_ACCESS_KEY_ID={} AWS_SECRET_ACCESS_KEY={} aws elasticbeanstalk describe-application-versions --application-name '{}' --version-label '{}' --region '{}'".format(
    #         access_key,
    #         secret_key,
    #         app_name,
    #         version_label,
    #         region
    #     )
    #     app_version = subprocess.check_output([cmd_app_version], shell=True)
    #
    #     upload_version = True
    #     if app_version:
    #         app_version_json = (json.loads(app_version.decode('ascii').strip()))
    #         if app_version_json and len(app_version_json['ApplicationVersions']) > 0:
    #             upload_version =  False
    #             print("Skipping application version upload. Version already exists.")
    #
    #     if upload_version:
    #         # Uploading application zip to elasticbeanstalk application versions
    #         print("Uploading application zip to elasticbeanstalk application versions...")
    #         cmd_upload_version = "AWS_ACCESS_KEY_ID={} AWS_SECRET_ACCESS_KEY={} aws elasticbeanstalk create-application-version --application-name '{}' --version-label '{}' --region '{}' --source-bundle S3Bucket='{}',S3Key='{}'".format(
    #             access_key,
    #             secret_key,
    #             app_name,
    #             version_label,
    #             region,
    #             s3_bucket,
    #             destination_jar_name
    #         )
    #         subprocess.run([cmd_upload_version], shell=True, check=True)
    #
    #     # Deploying application zip to elasticbeanstalk environment
    #     print("Deploying application zip to elasticbeanstalk environment:{}...".format(app_env))
    #     cmd_deploy = "AWS_ACCESS_KEY_ID={} AWS_SECRET_ACCESS_KEY={} aws elasticbeanstalk update-environment --environment-name {} --version-label '{}' --region '{}'".format(
    #         access_key,
    #         secret_key,
    #         app_env,
    #         version_label,
    #         region
    #     )
    #     subprocess.run([cmd_deploy], shell=True, check=True)
    #
    #     deployed_commit_id = check_application_health(service_name)
    #     verify_deployed_version(deployed_commit_id)
        print("deploy")
    except Exception as e:
         print("Exception occurred during application deployment:{}".format(e))
         raise e



def check_application_health(service_name):
    """
    To check whether the application url is up or not and fetch the deployed release commit id to compare
    :param health_check_url: Application health check URL
    :return:  deployed application commit id, if found
    """
    # health_check_url = os.getenv('HEALTHCHECK_URL', "")
    # if health_check_url:
    #     commit_id = ""
    #     delay_time = int(os.getenv('SVC_CHECK_INTERVAL', 30))
    #     threshold_time= int(os.getenv('SVC_CHECK_THRESHOLD', 300))
    #     num_of_hits=int(threshold_time/delay_time)
    #     hits = 0
    #     # Delay to have the application deployed on AWS, before verifying the health URL
    #     print("Waiting for {} to be up...".format(service_name))
    #     time.sleep(60)
    #     print("Waiting for {} to be up...".format(service_name))
    #     while hits < num_of_hits:
    #         hits += 1
    #         time.sleep(delay_time)
    #         print("Checking if {} is up...".format(service_name))
    #         response=requests.get(health_check_url)
    #         if response.status_code == 200:
    #             break
    #     if response.status_code != 200:
    #         raise Exception('Application has not been up since past {} seconds. Please check the deployed version...'.format(threshold_time))
    #
    #     if response:
    #         json_response = response.json()
    #         if json_response and json_response['git'] and json_response['git']['commit'] and json_response['git']['commit']['id'] and json_response['git']['commit']['id']['abbrev']:
    #             commit_id = json_response['git']['commit']['id']['abbrev']
    #
    #     print("Deployed application commit: {}".format(commit_id))
    #     return commit_id
    print("health check url")


def verify_deployed_version(deployed_commit_id):
    """
    To verify the deployed application commit id with the GoCD deployment
    :param deployed_commit_id:  Deployed application commit id
    # """
    # gocd_commit = os.environ['GO_PIPELINE_LABEL']
    # if gocd_commit:
    #     gocd_commit = gocd_commit.split("-")[-1]
    # print("Deployment Pipeline Commit:{}".format(gocd_commit))
    #
    # if not deployed_commit_id:
    #     print('Deployed commit version not found.')
    # if not gocd_commit:
    #     print('GoCD commit not found.')
    # if deployed_commit_id and gocd_commit:
    #     if deployed_commit_id == gocd_commit:
    #         print("Deployed application version matched the branch version.")
    #     elif deployed_commit_id != gocd_commit :
    #         raise Exception("Deployed application version doesn't match the branch version. Please check...")
    print("verify deployed")

def deploy_staging_my(deploy_env,version_label):
    version = re.findall(r'^([0-9]+.[0-9]+).', version_label)
    release_branch_name = "release-{}.0".format(version[0])
    if deploy_env in ["_MY", "_MY2"]:
        check_master_merge(release_branch_name)
        release_version = fetch_release_version(version_label)
        last_git_tag = check_last_tag()
        release_mesg = generate_release_mesg(last_git_tag)
        gen_tag(release_version, release_mesg, last_git_tag)
    elif deploy_env == "_STAGING":
        release_branch(release_branch_name)

def release_branch(release_branch):
    """
    To create the name of the release branch and fetch the version form gocd_label.
    If the branch name already exists in repo it just print the mesg branch  already created.
    :param gocd_label: Gocd label to fetch the version.
    """
    last_release_branch_cmd = "git ls-remote --heads origin | grep 'release-*' | tail -1 | grep -E -o 'release-[0-9]+.[0-9]+.[0-9]+'"
    last_release_branch = subprocess.check_output([last_release_branch_cmd], shell=True).decode('ascii').strip()
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
    print(release_branch_commit_Id)
    if not release_branch_commit_Id:
        raise Exception("Empty last release branch commit ID. Please check")
    checkout_master_cmd="git checkout master"
    subprocess.run([checkout_master_cmd], shell=True, check=True)
    check_master_cmd ="git branch --contains {} --points-at master".format(release_branch_commit_Id)
    check_master=subprocess.check_output([check_master_cmd], shell=True).decode('ascii').strip()
    if check_master != "* master":
        print(check_master)
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

def check_last_tag():
    """
    Checks the last release tag name with the current version name if both were same then it throws exception.
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

def gen_tag(release_version,release_mesg,last_git_tag):
    """
    To create and release the tag to the github
    :param release_version: lastest release verison name
    :param release_mesg: Mesg to be pushed with relese tag
    """
    if release_version == last_git_tag:
        print("Tag already created please check")
    else:
        create_tag_cmd="git tag {} -m '{}' ".format(release_version, release_mesg)
        subprocess.run([create_tag_cmd], shell=True, check=True)
        push_tag_cmd="git push origin {} ".format(release_version)
        subprocess.run([push_tag_cmd], shell=True, check=True)

if __name__ == "__main__":
    main()