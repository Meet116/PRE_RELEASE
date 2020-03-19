import subprocess
import os


def main():
    aws_access_key = os.environ['ACCESS_KEY']
    aws_secret_key = os.environ['SECRET_KEY']
    env_name = os.environ['ENV']
    health_status = ''
    check_color = ''
    while not health_status == "0k" and not check_color == "Green":
        check_color_cmd = "AWS_ACCESS_KEY_ID={} AWS_SECRET_ACCESS_KEY={} aws elasticbeanstalk describe-environment-health --environment-name {} --attribute-names All | grep 'Color' | cut -d ':' -f2".format(
            aws_access_key, aws_secret_key, env_name)
        check_color = subprocess.check_output([check_color_cmd], shell=True).decode('ascii').strip()
        check_color = check_color.replace('"', '').replace(',', '')
        health_status_cmd = "AWS_ACCESS_KEY_ID={} AWS_SECRET_ACCESS_KEY={} aws elasticbeanstalk describe-environment-health --environment-name {} --attribute-names All | grep 'Color' | cut -d ':' -f2".format(
            aws_access_key, aws_secret_key, env_name)
        health_status = subprocess.check_output([health_status_cmd], shell=True).decode('ascii').strip()
        health_status = health_status.replace('"', '').replace(',', '')
        print(check_color + "\n" + health_status)


if __name__ == '__main__':
    main()
