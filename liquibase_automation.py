import json
import subprocess
import os
import re


def main():
    skip_db = os.getenv('SKIP_DB', 'true').upper()
    gocd_label = os.environ['GO_PIPELINE_LABEL']
    version = re.findall(r'^([0-9]+.[0-9]+.[0-9]+).', gocd_label)
    file_path = "SQL/"
    filename_cmd = 'find {} -name "*{}*" -print | cut -d "/" -f2'.format(file_path, version[0])
    filename = subprocess.check_output([filename_cmd], shell=True).decode('ascii').strip()
    filename_with_path = file_path + "/" + filename
    if not filename:
        raise FileNotFoundError("File not found please check...")
    if skip_db == 'False':
        json_file = 'json_file/' + os.environ['JSON_FILE']
        check_file_status(json_file, filename, filename_with_path)
        execute_db(filename_with_path)


def check_file_status(json_file, filename, filename_with_path):
    """
    To check the file is new or not
    :param json_file: json file name
    :param filename: new file name
    :param filename_with_path: new file with path
    """
    with open(json_file, 'r') as f:
        data = json.load(f)
        filename_in_json = data["filename"]
    if filename != filename_in_json:
        new_file_found(json_file, filename)
        prepend_liquibase_format(json_file, filename_with_path)
        upload_to_s3(filename_with_path)
    else:
        fetch_from_s3(filename)
        check_difference(json_file, filename, filename_with_path)


def new_file_found(json_file, filename):
    """
    If the file is new update the json file with new file name and increases the minor by 1 and set patch to 0 in json file.
    :param json_file: json file name with path
    :param filename: sql file name
    """
    with open(json_file, 'r') as f:
        data = json.load(f)
        data["filename"] = filename
        minor = data["changeset"]["id"]["minor"]
        new_minor = int(minor) + 1
        data["changeset"]["id"]["minor"] = str(new_minor)
        data["changeset"]["id"]["patch"] = '0'
    with open(json_file, "w") as f:
        f.write(json.dumps(data))


def prepend_liquibase_format(json_file, filename_with_path):
    """
    If the file is run for the first time prepend the liquibase executable format into it.
    :param json_file: json file name with path
    :param filename_with_path: sql file name with path
    """
    changeset = fetch_id(json_file)
    with open(filename_with_path, 'r') as f:
        data = f.read()
    with open(filename_with_path, 'w') as f:
        f.write("--liquibase formatted sql {} \n".format(changeset) + data)


def fetch_id(json_file):
    """
    fetch the id and author name from the json file and create the message to insert in the file.
    :param json_file: json file name
    :return: changeset message for eg:- --changeset author:1.X.X
    """
    with open(json_file, 'r') as f:
        data = json.load(f)
        major = data["changeset"]["id"]["major"]
        minor = data["changeset"]["id"]["minor"]
        patch = data["changeset"]["id"]["patch"]
        id = "{}.{}.{}".format(major, minor, patch)
        author = data["changeset"]["author"]
    return " \n--changeset {}:{}\n".format(author, id)


def check_difference(json_file, filename, filename_with_path):
    """
    To get the line number from which the file is changed.
    :param json_file: json file name with path
    :param filename: sql file name
    :param filename_with_path: sql file name with path
    """
    dif_cmd = 'diff -wB S3/{} {} | grep "^[0-9]+*" | grep -E -o "[A-Za-z]+[0-9]+*" | grep -E -o "[0-9]+"'.format(
        filename, filename_with_path)
    dif = subprocess.check_output([dif_cmd], shell=True).decode('ascii').strip()
    dif = dif.split('\n')
    for i in range(len(dif)):
        if i == 0:
            value = int(dif[0]) - 1
            update_json(json_file)
            edit_file_with_changeset(value, filename_with_path, json_file)
        else:
            value = int(dif[i]) + (i * 2) - 1
            update_json(json_file)
            edit_file_with_changeset(value, filename_with_path, json_file)
    upload_to_s3(filename_with_path)


def update_json(json_file):
    """
    Update the json file and increment the patch by 1.
    :param json_file: json file name with path
    """
    with open(json_file, 'r') as f:
        data = json.load(f)
        old_patch = data["changeset"]["id"]["patch"]
        new_patch = int(old_patch) + 1
        data["changeset"]["id"]["patch"] = str(new_patch)
    with open("changeset.json_file", "w") as f:
        f.write(json.dumps(data))


def edit_file_with_changeset(line_index, filename_with_path, json_file):
    """
    Edit the file add the changeset id and author in the sql file
    :param line_index: On which line the file is changed
    :param filename_with_path: sql file name with path
    :param json_file: json file name
    """
    f = open(filename_with_path, "r")
    contents = f.readlines()
    f.close()
    message = fetch_id(json_file)
    print(line_index)
    contents.insert(int(line_index), message)
    f = open(filename_with_path, "w")
    contents = "".join(contents)
    f.write(contents)
    f.close()


def upload_to_s3(filename_with_path):
    """
    To upload the updated file to the S# bucket
    :param filename_with_path: sql file name with path
    """
    print("Upload to s3." + filename_with_path)


def fetch_from_s3(filename):
    """
    To fetch the file from the s3 bucket
    :param filename: sql file name
    """
    print("Fetch file from s3" + filename)


def execute_db(filename_with_path):
    """
    Execute the liquibase command for database.
    :param filename_with_path: sql file name with path
    """

    # URL filename and db name to be change
    url = os.environ['DB_URL']
    db_name = os.environ['DB_NAME']
    if not url or not filename_with_path:
        raise ValueError(" Filename or database url empty")
    # --url format to be changed and classpath also according to the installation
    liquibase_command = "liquibase --changeLogFile={} --url jdbc:mysql://{}/{} --classpath=/usr/apps/Liquibase-3.8.6-bin/liquibase/liquibase.jar update".format(
        filename_with_path, url, db_name)
    subprocess.run([liquibase_command], shell=True, check=True)


if __name__ == "__main__":
    main()
