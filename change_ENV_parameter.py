import requests
import os
import time

def main():
    try:
       actuator_url = os.environ["ACTUATOR_URL"]
       actuator_commit_id=check_actuator_url_and_commit_id(actuator_url)
       check_commit_id(actuator_commit_id)
    except Exception as e:
        print("exception{}".format(e))
        raise e

def check_actuator_url_and_commit_id(actuator_url):
    """
    To check the actuator url is up or not and fetch the last release commit id from that
    :param actuator_url: Url of the actuator
    :return:  Actuator commit id from actuator URL
    """
    delay_time = int(os.getenv('SVC_CHECK_INTERVAL','2'))
    threshold_time=int(os.getenv('SVC_CHECK_THRESHOLD','6'))
    num_of_hits=int(threshold_time/delay_time)
    hits = 0
    while hits <= num_of_hits-1:
        hits = hits + 1
        time.sleep(delay_time)
        response=requests.get(actuator_url)
        if response.status_code == 200:
            break
    if response.status_code != 200:
        raise Exception('Application down since past {} seconds. Please check'.format(threshold_time))
    if not response and not response.json()['git']['commit']['id']['abbrev']:
        raise Exception('Empty mesg in response commit id not found from actuator url')
    return response.json()['git']['commit']['id']['abbrev']

def check_commit_id(actuator_commit_id):
    """
    To verify the commit id of actuator with gocd label commt id
    :param actuator_commit_id:  Commit id form actuator URL
    """
    gocd_label_commit_id = os.environ['GO_PIPELINE_LABEL'].split("-")[-1]
    print(gocd_label_commit_id, actuator_commit_id)
    if not actuator_commit_id:
        raise Exception('Empty actuator commit id please check...')
    if not gocd_label_commit_id:
        raise Exception('Empty gocd label commit id please check...')
    if actuator_commit_id != gocd_label_commit_id :
        raise Exception("Latest release were not updated on server please check....")

if __name__ == "__main__":
    main()