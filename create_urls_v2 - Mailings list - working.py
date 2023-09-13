import requests
import time
import hashlib
import certifi
from typing import List, Dict
from secrets import api_key, team_id, list_id2, yourls_signature
import urllib3
import json

#note the following line could hinder debugging
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


headers = {"Authorization": api_key}

def get_all_tasks() -> List[Dict]:
    all_tasks = []
    page = 0
    while True:
        url = f"https://api.clickup.com/api/v2/list/{list_id2}/task?page={page}"
        response = requests.get(url, headers=headers)
        tasks = response.json()["tasks"]
        if not tasks:
            break
        all_tasks.extend(tasks)
        page += 1
    print(f"Total number of tasks: {len(all_tasks)}")
    return all_tasks


def get_custom_field_value(task, field_id):
    for field in task["custom_fields"]:
        if field["id"] == field_id:
            if field["type"] == "drop_down":
                selected_orderindex = field.get("value")  # Use .get() instead of direct access
                if selected_orderindex is not None:
                    for option in field["type_config"]["options"]:
                        if option["orderindex"] == selected_orderindex:
                            return option["name"]
                else:
                    # Find the option with "SUBSCRIBE_ME" as the name and return it
                    for option in field["type_config"]["options"]:
                        if option["name"] == "SUBSCRIBE_ME":
                            update_custom_field_value(task["id"], field_id, option["orderindex"])  # Update the custom field value
                            return option["name"]
            else:
                return field.get("value")  # Use .get() instead of direct access
    return None


def update_custom_field_value(task_id, field_id, orderindex):
    url = f"https://api.clickup.com/api/v2/task/{task_id}/field/{field_id}"
    payload = {
        "value": orderindex
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": api_key
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        print(f"Successfully updated custom field for task ID {task_id}")
    else:
        print(f"Error updating custom field for task ID {task_id}: {response.status_code}")
        return


def create_short_url(long_url: str) -> str:
    api_url = "https://bump.tk/yourls-api.php"
    timestamp = int(time.time())
    signature = hashlib.md5((str(timestamp) + yourls_signature).encode("utf-8")).hexdigest()

    payload = {
        "signature": signature,
        "timestamp": timestamp,
        "action": "shorturl",
        "url": long_url,
        "format": "json",
    }

    retries = 3
    for attempt in range(retries):
        try:
            response = requests.get(api_url, params=payload, verify=False, timeout=10)
            response_json = json.loads(response.text)

            if response.status_code == 200:
                return response_json["shorturl"]
            else:
                error_message = response.text
                if "already exists in database" in error_message:
                    short_url = response_json["url"]["keyword"]
                    short_url = f"https://bump.tk/{short_url}"
                    print(f"URL already exists in the database. Using existing short URL: {short_url}")
                    return short_url
                else:
                    raise Exception(f"Failed to create short URL: {error_message}")
        except requests.exceptions.ConnectTimeout as e:
            print(f"Request attempt {attempt + 1} timed out: {e}")
            if attempt < retries - 1:
                delay = (attempt + 1) * 5  # increase delay between retries
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                raise e


def update_field(task_id, field_id, email, preferences, task_custom_id, task_name):
    long_url = f"https://forms.clickup.com/20419954/f/kf5bj-36908/RW89FKBMHVRM0RMQP2?Email={email}&Preferences={preferences}&ID={task_custom_id}"
    short_url = create_short_url(long_url)

    if short_url is None:
        print(f"Error updating 'FORM 2 as URL' field for task ID {task_id}: URL shortening failed")
        return

    url = f"https://api.clickup.com/api/v2/task/{task_id}/field/{field_id}"
    payload = {
        "value": short_url
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": api_key
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        print(f"Successfully updated 'FORM 2 as URL' field for task {task_name} (ID {task_id}): {short_url}")
    else:
        print(f"Error updating 'FORM 2 as URL' field for task ID {task_id}: {response.status_code}")
        return

    # Update task status to 'urls updated'
    status_name = "urls updated"
    url = f"https://api.clickup.com/api/v2/task/{task_id}"
    payload = {
        "status": status_name
    }
    response = requests.put(url, json=payload, headers=headers)
    if response.status_code == 200:
        print(f"Successfully updated task status to '{status_name}' for task {task_name} (ID {task_id})")
    else:
        print(f"Error updating task status for task {task_name} (ID {task_id}): {response.status_code}")



def main():
    tasks = get_all_tasks()
    create_urls_status = "create urls"
    tasks_with_create_urls_status = [task for task in tasks if task["status"]["status"] == create_urls_status]
    
    total_tasks = len(tasks_with_create_urls_status)
    print(f"Total number of tasks with status 'create urls': {total_tasks}")

    api_call_counter = 0
    email_field_id = "2dcddc3f-521d-439d-bb9a-fa1e9b804273"
    preferences_field_id = "9f85dcab-8b2e-4c0f-8175-d8a1d1f010ce"
    form2_field_id = "1b18be99-285f-4020-8f65-28a8e757f50b"

    for task in tasks_with_create_urls_status:
        print(f"Updating task with 'create urls' status: Task ID - {task['id']}, Task name - {task['name']}")
        email = get_custom_field_value(task, email_field_id)
        preferences = get_custom_field_value(task, preferences_field_id)

        update_field(task["id"], form2_field_id, email, preferences, task["id"], task["name"])
        api_call_counter += 1
        if api_call_counter > 90:
            time.sleep(0.6)  # Add a delay of 0.6 seconds between API calls after 90 calls


if __name__ == "__main__":
    main()
