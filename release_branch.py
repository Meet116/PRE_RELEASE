import os
import re
import subprocess


def main():
    try:
        deploy_env = "_" + os.environ['DEPLOY_TO'].upper()
        if deploy_env == "_STAGING":
            release_branch()


    except Exception as e:
        print("Exception occurred during application deployment stage:{}".format(e))
        raise e
def release_branch():
    gocd_label = os.environ['GO_PIPELINE_LABEL']
    version = re.findall(r'^([0-9]+.[0-9]+.[0-9]+).', gocd_label)
    if not version:
        raise Exception("Please check the label .")
    else:
        last_release_branch_cmd = "git ls-remote --heads origin | grep release-* | tail -1 | grep -E -o 'release-[0-9]+.[0-9]+.[0-9]+'"
        last_release_branch = subprocess.check_output([last_release_branch_cmd], shell=True).decode('ascii').strip()
        release_branch = "release-{}".format(version[0])
        patch=re.findall(r'([0-9]+$)',release_branch)
        print(patch[0])
        if last_release_branch == release_branch or patch[0] != '0':
            print("Branch already created")
        else:
            create_release_branch(release_branch)

def create_release_branch(release_branch):
    release_branch_cmd = "git checkout -b {}".format(release_branch)
    subprocess.run([release_branch_cmd], shell=True, check=True)
    release_branch_push_cmd = "git push origin {}".format(release_branch)
    subprocess.run([release_branch_push_cmd], shell=True, check=True)




if __name__ == "__main__":
    main()