import requests
import time
from secrets import api_key, team_id, list_id

headers = {
    "Authorization": api_key,
    "Content-Type": "application/json"
}

api_calls = 0

def pause_if_needed():
    global api_calls
    if api_calls >= 98:
        print("Pausing due to max API calls.")
        time.sleep(65)
        api_calls = 0

def get_all_tasks():
    all_tasks = []
    page = 0
    while True:
        url = f"https://api.clickup.com/api/v2/team/{team_id}/task"
        params = {
            "list_ids[]": list_id,
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


def add_tag_to_task(task_id, tag_name):
    global api_calls
    url = f"https://api.clickup.com/api/v2/task/{task_id}/tag/{tag_name}"
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    api_calls += 1
    pause_if_needed()

def find_and_tag_duplicate_tasks(tasks):
    task_names = {}
    duplicate_tasks = []
    for task in tasks:
        task_name = task["name"]
        if task_name in task_names:
            duplicate_task_id = task["id"]
            print(f"Found duplicate: Task ID - {duplicate_task_id}, Task name - {task_name}")
            add_tag_to_task(duplicate_task_id, "possible_duplicate")
            duplicate_tasks.append(duplicate_task_id)
        else:
            task_names[task_name] = task["id"]
    return duplicate_tasks

tasks = get_all_tasks()
print(f"Total number of tasks: {len(tasks)}")

duplicate_tasks = find_and_tag_duplicate_tasks(tasks)
print(f"Total number of duplicate tasks: {len(duplicate_tasks)}")
