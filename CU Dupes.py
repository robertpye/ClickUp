import requests
import random
import string
import sys
from typing import List, Dict
from secrets import api_key, team_id, list_id2

headers = {"Authorization": api_key}

def get_all_tasks() -> List[Dict]:
    url = f"https://api.clickup.com/api/v2/list/{list_id2}/task"
    response = requests.get(url, headers=headers)
    tasks = response.json()["tasks"]
    print(f"Total number of tasks: {len(tasks)}")
    return tasks

def get_custom_field_value(task, field_id):
    for field in task["custom_fields"]:
        if field["id"] == field_id:
            if field["type"] == "drop_down":
                selected_orderindex = field["value"]
                if selected_orderindex is not None:
                    for option in field["type_config"]["options"]:
                        if option["orderindex"] == selected_orderindex:
                            return option["name"]
                else:
                    return ""
            else:
                return field["value"]
    return None

def update_field(task_id, field_id, email, preferences, task_custom_id):
    url = f"https://api.clickup.com/api/v2/task/{task_id}/field/{field_id}"

    query = {
        "custom_task_ids": "yes",
        "team_id": "20419954"
    }

    form2_url = f"https://forms.clickup.com/20419954/f/kf5bj-36908/RW89FKBMHVRM0RMQP2?Email={email}&Preferences={preferences}&ID={task_custom_id}"

    payload = {
        "value": form2_url
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": api_key
    }

    response = requests.post(url, json=payload, headers=headers, params=query)

    if response.status_code == 200:
        print(f"Successfully updated 'FORM 2 as URL' field for task ID {task_id}: {form2_url}")
    else:
        print(f"Error updating 'FORM 2 as URL' field for task ID {task_id}: {response.status_code}")

def main():
    tasks = get_all_tasks()

    create_urls_status = "create urls"
    tasks_with_create_urls_status = [task for task in tasks if task["status"]["status"] == create_urls_status]

    print(f"Total number of tasks with status '{create_urls_status}': {len(tasks_with_create_urls_status)}")

    email_field_id = "2dcddc3f-521d-439d-bb9a-fa1e9b804273"
    preferences_field_id = "9f85dcab-8b2e-4c0f-8175-d8a1d1f010ce"  # Updated to the correct ID
    form2_field_id = "1b18be99-285f-4020-8f65-28a8e757f50b"

    for task in tasks_with_create_urls_status:
        print(f"Updating task with '{create_urls_status}' status: Task ID - {task['id']}, Task name - {task['name']}")

        email = get_custom_field_value(task, email_field_id)
        preferences = get_custom_field_value(task, preferences_field_id)

        update_field(task["id"], form2_field_id, email, preferences, task["id"])

if __name__ == "__main__":
    main()
