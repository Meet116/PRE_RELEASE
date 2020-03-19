# To automate the mysql scripts with liquibase.


import json
import subprocess
import os
import re


def main():
    skip_db = os.getenv('SKIP_DB', 'true').upper()
    gocd_label = os.environ['GO_PIPELINE_LABEL']
    version = re.findall(r'^([0-9]+.[0-9]+.[0-9]+).', gocd_label) or re.findall(r'^(sprint)*', gocd_label)
    sql_local_path = os.environ['SQL_FILE_PATH']
    aws_access_key = os.environ['ACCESS_KEY']
    aws_secret_key = os.environ['SECRET_KEY']
    bucket_name = os.environ['BUCKET_NAME']
    bucket_folder = os.environ['BUCKET_FOLDER']
    jsonfile = "ecv-release/database/sql/liquibase-changelog.json"
    if skip_db == 'FALSE':
        check_json_file(aws_access_key, aws_secret_key, bucket_name, jsonfile, bucket_folder)
        if version[0] == 'sprint':
            find_file = "ls -Art {} | tail -n 1".format(sql_local_path)
            filename = subprocess.check_output([find_file], shell=True).decode('ascii').strip()
            semantic_version = fetch_semantic_version(filename)
            check_file(sql_local_path, aws_access_key, aws_secret_key, bucket_name, jsonfile, semantic_version,
                       filename, bucket_folder)
        else:
            filename_cmd = 'find {} -name "*{}*" -print | cut -d "/" -f2'.format(sql_local_path, version[0])
            filename = subprocess.check_output([filename_cmd], shell=True).decode('ascii').strip()
            check_file(sql_local_path, aws_access_key, aws_secret_key, bucket_name, jsonfile, version[0], filename,
                       bucket_folder)
    else:
        print("Skipping execution of database")


def check_json_file(aws_access_key, aws_secret_key, bucket_name, jsonfile, bucket_folder):
    """
    Checks json file present on local or not if not then it pull from s3 storage.
    :param aws_access_key: Aws access key.
    :param aws_secret_key: Aws secret key.
    :param bucket_name: S3 bucket name.
    :param jsonfile: json file name with path
    :param bucket_folder: bucket folder.
    """
    if not os.path.isfile(jsonfile):
        fetch_json_cmd = "AWS_ACCESS_KEY_ID = {} AWS_SECRET_ACCESS_KEY = {} aws s3 cp s3://{}/{}/liquibase-changelog.json  ecv-releases/databases/sql/liquibase-changelog.json".format(
            aws_access_key, aws_secret_key, bucket_name, bucket_folder)
        subprocess.run([fetch_json_cmd], shell=True, check=True)


def check_file(sql_local_path, aws_access_key, aws_secret_key, bucket_name, jsonfile, semantic_version, filename,
               bucket_folder):
    """
    Check the file it is new or old one.
    :param sql_local_path: Sql local file path.
    :param aws_access_key: Aws access key.
    :param aws_secret_key: Aws secret key.
    :param bucket_name: S3 bucket name.
    :param jsonfile: jsonfile with path.
    :param semantic_version: semantic version format.
    :param filename: sql filename.
    :param bucket_folder: bucket folder path
    """
    fetch_sql_file_cmd = "AWS_ACCESS_KEY_ID = {} AWS_SECRET_ACCESS_KEY = {} aws s3 cp s3://{}/{}/{}/{} .".format(
        aws_access_key, aws_secret_key, bucket_name, bucket_folder, semantic_version, filename)
    subprocess.run([fetch_sql_file_cmd], shell=True)
    sql_file_with_path = sql_local_path + "/" + filename
    if not os.path.exists(filename):
        liquibase_sql_file_cmd = "cp {} liquibase-{}".format(sql_file_with_path, filename)
        subprocess.check_output([liquibase_sql_file_cmd], shell=True).decode('ascii').strip()
        liquibase_sql_file = "liquibase-{}".format(filename)
        update_json_new_file(jsonfile, semantic_version)
        prepend_liquibase_format(jsonfile, liquibase_sql_file)
    else:
        liquibase_sql_file = "liquibase-{}".format(filename)
        fetch_liquibase_file(aws_access_key, aws_secret_key, liquibase_sql_file, bucket_name, semantic_version,
                             bucket_folder)
        check_difference(jsonfile, liquibase_sql_file, sql_file_with_path, filename)
    execute_liquibase(liquibase_sql_file)
    upload_to_s3(aws_access_key, aws_secret_key, bucket_name, sql_file_with_path, semantic_version, liquibase_sql_file,
                 bucket_folder)


def fetch_semantic_version(filename):
    """
    Fetch the semantic format from the filename.
    :param filename: sql file name.
    :return: semantic version
    """
    version = re.findall(r'-([0-9]+.[0-9]+.[0-9]+).*', filename)
    return version[0]


def update_json_new_file(jsonfile, fetch_version):
    """
    Update the json file if new file found
    :param jsonfile: json file with path
    :param fetch_version: semantic version
    """
    with open(jsonfile, 'r') as f:
        data = json.load(f)
        data["changeset"]["id"]["version"] = fetch_version
        data["changeset"]["id"]["incremental"] = '0'
    with open(jsonfile, "w") as f:
        f.write(json.dumps(data))


def prepend_liquibase_format(jsonfile, liquibase_sql_file):
    """
    Prepend the liquibase format in the liquibase sql file.
    :param jsonfile: json filename with path.
    :param liquibase_sql_file: liquibase file name
    """
    changeset = fetch_id(jsonfile)
    with open(liquibase_sql_file, 'r') as f:
        data = f.read()
    with open(liquibase_sql_file, 'w') as f:
        f.write("--liquibase formatted sql {} \n".format(changeset) + data)


def fetch_id(jsonfile):
    """
    Fetch the changeset id from jsonfile
    :param jsonfile: jsonfile with path
    :return: changeset id mesg.
    """
    with open(jsonfile, 'r') as f:
        data = json.load(f)
        version = data["changeset"]["id"]["version"]
        incremental = data["changeset"]["id"]["incremental"]
        id = "{}.{}".format(version, incremental)
        author = data["changeset"]["author"]
    return " \n--changeset {}:{}\n".format(author, id)


def fetch_liquibase_file(aws_access_key, aws_secret_key, liquibase_sql_file, bucket_name, semantic_version,
                         bucket_folder):
    """
    If the file is old then fetch the liquibase file from the aws s3 bucket.
    :param aws_access_key: Aws access key
    :param aws_secret_key: Aws secret key
    :param liquibase_sql_file: Liquibase sql file name.
    :param bucket_name: S3 bucket name.
    :param semantic_version: Semantic version
    :param bucket_folder: S3 bucket folder path
    """
    liquibase_sql_file = "AWS_ACCESS_KEY_ID = {} AWS_SECRET_ACCESS_KEY = {} aws s3 cp s3://{}//{}/liquibase/{} .".format(
        aws_access_key, aws_secret_key, bucket_name, bucket_folder, semantic_version, liquibase_sql_file, )
    subprocess.run([liquibase_sql_file], shell=True, check=True)


def check_difference(jsonfile, liquibase_sql_file, sql_file_with_path, filename):
    """
    Checks which new line add to the sql file , of the file reruns.
    :param jsonfile: json file with path
    :param liquibase_sql_file: liquibase file name.
    :param sql_file_with_path: sql file with path
    :param filename: sql file name
    """
    check_diff_cmd = "grep -Fxvf {} {}".format(filename, sql_file_with_path)
    diff = subprocess.check_output([check_diff_cmd], shell=True).decode('ascii').strip()
    if diff:
        update_json(jsonfile)
        append_changes(diff, liquibase_sql_file, jsonfile)


def update_json(jsonfile):
    """
    Update the json file and increment the incremental by 1.
    :param jsonfile: json file name with path
    """
    with open(jsonfile, 'r') as f:
        data = json.load(f)
        incremental = data["changeset"]["id"]["incremental"]
        new_incremental = int(incremental) + 1
        print(new_incremental)
        data["changeset"]["id"]["incremental"] = str(new_incremental)
    with open(jsonfile, "w") as f:
        f.write(json.dumps(data))


def append_changes(diff, liquibase_sql_file, jsonfile):
    """
    Append the changes in the liquibase file with the changeset id and author name .
    :param diff: diff in the file
    :param liquibase_sql_file: liquibase file name
    :param jsonfile: json file with path
    """
    changeset_id = fetch_id(jsonfile)
    f = open(liquibase_sql_file, 'a')
    f.write('\n' + changeset_id + '\n' + diff)
    f.close()


def execute_liquibase(liquibase_sql_file):
    """
    Execute the liquibase command.
    :param liquibase_sql_file:  liquibase file name
    """
    deploy_env = "_" + os.environ['DEPLOY_TO'].upper()
    url = os.environ['URL' + deploy_env]
    if not url or not liquibase_sql_file:
        raise ValueError(" Filename or database url empty")
    # Change the class path as per liquibase installation
    liquibase_command = "liquibase --changeLogFile={} --url {} --classpath=/usr/apps/Liquibase-3.8.6-bin/liquibase/liquibase.jar update".format(
        liquibase_sql_file, url)
    subprocess.run([liquibase_command], shell=True, check=True)


def upload_to_s3(aws_access_key, aws_secret_key, bucket_name, sql_file_with_path, semantic_version, liquibase_sql_file,
                 bucket_folder):
    """
    Upload json file , sql file and liquibase sql file on S3 bucket.
    :param aws_access_key: Aws access key
    :param aws_secret_key: Aws secret key
    :param bucket_name: S3 bucket name
    :param sql_file_with_path: sql file with path
    :param semantic_version: semantic version
    :param liquibase_sql_file: liquibase file name
    :param bucket_folder: bucket folder path
    """
    upload_json_file_cmd = "AWS_ACCESS_KEY_ID = {} AWS_SECRET_ACCESS_KEY = {} aws s3 cp ecv-releases/databases/sql/liquibase-changelog.json s3://{}/{}/".format(
        aws_access_key, aws_secret_key, bucket_name, bucket_folder)
    subprocess.run([upload_json_file_cmd], shell=True, check=True)
    upload_sql_file_cmd = "AWS_ACCESS_KEY_ID = {} AWS_SECRET_ACCESS_KEY = {} aws s3 cp {} s3://{}/{}/{}/".format(
        aws_access_key, aws_secret_key, sql_file_with_path, bucket_name, bucket_folder, semantic_version)
    subprocess.run([upload_sql_file_cmd], shell=True, check=True)
    upload_liquibase_sql_file_cmd = "AWS_ACCESS_KEY_ID = {} AWS_SECRET_ACCESS_KEY = {} aws s3 cp {} s3://{}/{}/{}/liquibase/".format(
        aws_access_key, aws_secret_key, liquibase_sql_file, bucket_name, bucket_folder, semantic_version)
    subprocess.run([upload_liquibase_sql_file_cmd], shell=True, check=True)
    fetch_date = "date +'%d-%m-%Y-%H:%M'"
    current_date = subprocess.check_output([fetch_date], shell=True).decode('ascii').strip()
    liquibase_backup_file_cmd = "cp {} {}-{}".format(liquibase_sql_file, current_date, liquibase_sql_file)
    subprocess.run([liquibase_backup_file_cmd], shell=True, check=True)
    liquibase_backup_sql_file = "{}-{}".format(current_date, liquibase_sql_file)
    upload_liquibase_backup_sql_file_cmd = "AWS_ACCESS_KEY_ID = {} AWS_SECRET_ACCESS_KEY = {} aws s3 cp {} s3://{}/{}/{}/liquibase/".format(
        aws_access_key, aws_secret_key, liquibase_backup_sql_file, bucket_name, bucket_folder, semantic_version)
    subprocess.run([upload_liquibase_backup_sql_file_cmd], shell=True, check=True)


if __name__ == "__main__":
    main()
