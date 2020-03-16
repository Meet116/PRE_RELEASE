import json
import subprocess
import os


def main():
    try:
        skip_db = os.getenv('SKIP_DB', 'true').upper()
        new_filename = os.environ['FILENAME']
        if not os.path.isfile(new_filename):
            raise FileNotFoundError("File name not exists please check")
        if skip_db == 'FALSE':
            # change the json file path
            json_file = 'json_file/' + os.environ['JSON_FILE']
            check_file_availability(json_file, new_filename)
            # execute_db()
        else:
            print(" Skipping database execution")
    except Exception as e:
        print("Exception occured while executing the database execution script")


def check_file_availability(json_file, check_filename):
    """
    To check the file is new or not
    :param json_file: json file name
    :param check_filename: new file name
    """
    with open(json_file, 'r') as f:
        data = json.load(f)
        filename = data["filename"]
    if filename != check_filename:
        new_file_found(json_file, check_filename)
        prepend_liquibase_format(json_file, check_filename)
        upload_to_s3(check_filename)
    else:
        fetch_from_s3(check_filename)
        check_difference(json_file, check_filename)


def new_file_found(json_file, filename):
    """
    If the file is new update the json file with new file name and increases the minor by 1 and set patch to 0 in json file.
    :param json_file: json file name
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


def prepend_liquibase_format(json_file, filename):
    """
    If the file is run for the first time prepend the liquibase executable format into it.
    :param json_file: json file name
    :param filename: sql file name
    """
    changeset = fetch_id(json_file)
    with open("SQL/" + filename, 'r') as f:
        data = f.read()
    with open("SQL/" + filename, 'w') as f:
        f.write("--liquibase formatted sql {} \n".format(changeset) + data)


def upload_to_s3(filename):
    """
    To upload the updated file to the S# bucket
    :param filename: sql file name
    """
    print("Upload to s3." + filename)


def fetch_from_s3(filename):
    """
    To fetch the file from the s3 bucket
    :param filename: sql file name
    """
    print("Fetch file from s3" + filename)


def check_difference(json_file, filename):
    """
    To get the line number from which the file is changed.
    :param json_file: json file name
    :param filename: sql file name
    """
    dif_cmd = 'diff -wB S3/{} SQL/{} | grep "^[0-9]+*" | grep -E -o "[A-Za-z]+[0-9]+*" | grep -E -o "[0-9]+"'.format(
        filename, filename)
    dif = subprocess.check_output([dif_cmd], shell=True).decode('ascii').strip()
    dif = dif.split('\n')
    for i in range(len(dif)):
        if i == 0:
            value = int(dif[0]) - 1
            update_json(json_file)
            edit_file_with_changeset(value, filename, json_file)
        else:
            value = int(dif[i]) + (i * 2) - 1
            update_json(json_file)
            edit_file_with_changeset(value, filename, json_file)
    upload_to_s3(filename)


def edit_file_with_changeset(line_index, filename, json_file):
    """
    Edit the file add the changeset id and author in the sql file
    :param line_index: On which line the file is changed
    :param filename: sql file name
    :param json_file: json file name
    """
    f = open("SQL/" + filename, "r")
    contents = f.readlines()
    f.close()
    message = fetch_id(json_file)
    print(line_index)
    contents.insert(int(line_index), message)
    f = open("SQL/" + filename, "w")
    contents = "".join(contents)
    f.write(contents)
    f.close()


def update_json(json_file):
    """
    Update the json file and increment the patch by 1.
    :param json_file: json file name
    """
    with open(json_file, 'r') as f:
        data = json.load(f)
        old_patch = data["changeset"]["id"]["patch"]
        new_patch = int(old_patch) + 1
        data["changeset"]["id"]["patch"] = str(new_patch)
    with open("changeset.json_file", "w") as f:
        f.write(json.dumps(data))


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


def execute_db():
    """
    Execute the liquibase command for database.
    """

    # URL filename and db name to be change
    url = os.environ['DB_URL']
    filename = os.environ['FILENAME']
    db_name = os.environ['DB_NAME']
    if not url or not filename:
        raise ValueError(" Filename or database url empty")
    # Changelog file to be change , --url format to be changed and classpath also according to the installation
    liquibase_command = "liquibase --changeLogFile=/path/to/sqlfile/{} --url jdbc:mysql://{}/{} --classpath=/usr/apps/Liquibase-3.8.6-bin/liquibase/liquibase.jar update".format(
        filename, url, db_name)
    subprocess.run([liquibase_command], shell=True, check=True)


if __name__ == "__main__":
    main()
