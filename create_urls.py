import requests
import time
from secrets import api_key, team_id, list_id2

headers = {"Authorization": api_key}

def get_all_tasks():
    all_tasks = []
    page = 0
    while True:
        url = f"https://api.clickup.com/api/v2/team/{team_id}/task"
        params = {
            "list_ids[]": list_id2,
            "page": page
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        tasks = response.json()["tasks"]
        if not tasks:
            break
        all_tasks.extend(tasks)
        page += 1
    return all_tasks

def update_email(task, new_email):
    email_field_id = None

    for field in task['custom_fields']:
        if field['name'] == 'Email':
            email_field_id = field['id']
            break

    if email_field_id:
        url = f"https://api.clickup.com/api/v2/task/{task['id']}/field/{email_field_id}"
        payload = {"value": new_email}
        response = requests.put(url, headers=headers, json=payload)

        if response.status_code == 200:
            print(f"Successfully updated email for task ID {task['id']}")
        else:
            print(f"Error updating email for task ID {task['id']}: {response.status_code}")
            if response.status_code != 404:
                print(response.json())

def main():
    tasks = get_all_tasks()
    print(f"Total number of tasks: {len(tasks)}")

    tasks_to_update = [task for task in tasks if task["status"]["status"] == "create urls"]

    print(f"Total number of tasks with status 'create urls': {len(tasks_to_update)}")

    if tasks_to_update:
        first_task = tasks_to_update[0]

        print(f"First task with 'create urls' status: Task ID - {first_task['id']}, Task name - {first_task['name']}")

        update_email(first_task, "spoof@spoof.com")

if __name__ == "__main__":
    main()
