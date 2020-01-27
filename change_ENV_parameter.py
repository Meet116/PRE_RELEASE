import requests
import json
from copy import deepcopy
import os
import time

def main():
    try:
       change_parameter_value()
       actuator_url = os.environ["ACTUATOR_URL"]
       check_actuator_url(actuator_url)
       actuator_commit_id = get_commit_id(actuator_url)
       check_commit_id(actuator_commit_id)

    except Exception as e:
        print("exception{}".format(e))
        raise e

#To change the parameter value of the pipeline
def change_parameter_value():
    gocd_pipeline_name = os.environ['GO_PIPELINE_NAME']
    gocd_url = "http://username:password@localhost:8153/go/api/admin/pipelines/{}".format(gocd_pipeline_name) #gocd-URL Need to find the solution for gocd username and password
    print(gocd_url)
    response = requests.get(gocd_url, headers={
        'Accept': 'application/vnd.go.cd.v10+json'})  # Change headers={'Accept': 'application/vnd.go.cd.v5+json'} for gocd version 18.6.0
    Etag_respose = requests.get(gocd_url, headers={
        'Accept': 'application/vnd.go.cd.v10+json'})  # Change headers={'Accept': 'application/vnd.go.cd.v5+json'} for gocd version 18.6.0
    if response.status_code != 200:
        raise Exception('GET /tasks/ {}'.format(response.status_code))
    update_mesg = deepcopy(response.json())
    for i in update_mesg['parameters']:
        if i['name'] == 'RELEASE':
            i['value'] = 'abc'
    print(Etag_respose.headers.get('Etag'))
    update_respose_header = {'Accept': 'application/vnd.go.cd.v10+json', 'Content-Type': 'application/json',
                             'If-Match': '{}'.format(Etag_respose.headers.get(
                                 'Etag'))}  # Change headers={'Accept': 'application/vnd.go.cd.v5+json'} for gocd version 18.6.0
    update_resp = requests.put(gocd_url, data=json.dumps(update_mesg), headers=update_respose_header)
    if update_resp.status_code != 200:
        raise Exception('PUT /tasks/ {}'.format(response.status_code))

def check_actuator_url(actuator_url):
    delay_time = int(os.environ['SVC_CHECK_INTERVAL'])
    thresold_time=int(os.environ['SVC_CHECK_THRESHOLD'])
    if not delay_time or not thresold_time:
        raise Exception("Please define the Interval and Thresold time in env variables.")
    num_of_hits=int(thresold_time/delay_time)
    tmp = 0
    while tmp <= num_of_hits-1:
        tmp = tmp + 1
        time.sleep(delay_time)
        response=requests.head(actuator_url)
        if response.status_code == 200:
            break
    if response.status_code != 200:
        raise Exception('Website is not up status code - {}'.format(response.status_code))

def get_commit_id(actuator_url):
    response = requests.get(actuator_url)
    return response.json()['git']['commit']['id']['abbrev']

def check_commit_id(actuator_commit_id):
    gocd_label_commit_id = os.environ['GO_PIPELINE_LABEL'].split("-",2)
    if actuator_commit_id != gocd_label_commit_id :
        raise Exception("Latest release were not updated on server please check....")

if __name__ == "__main__":
    main()