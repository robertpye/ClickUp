import requests
import time
from secrets import api_key, team_id, list_id1, list_id2, list_id3

headers = {"Authorization": api_key}


def get_all_tasks():
    all_tasks = []
    page = 0
    while True:
        url = f"https://api.clickup.com/api/v2/team/{team_id}/task"
        params = {
            "list_ids[]": [list_id1, list_id2, list_id3],
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



def find_duplicate_tasks(tasks):
    task_names = {}
    duplicate_tasks = []

    for task in tasks:
        task_name = task["name"].strip().lower()
        if task_name in task_names:
            task_names[task_name].append(task)
        else:
            task_names[task_name] = [task]

    for task_name in task_names:
        if len(task_names[task_name]) > 1:
            duplicate_tasks.extend(task_names[task_name])

    return duplicate_tasks


def add_possible_duplicate_tag(task_id):
    url = f"https://api.clickup.com/api/v2/task/{task_id}/tag/possible_duplicate"
    response = requests.post(url, headers=headers)
    response.raise_for_status()


def main():
    tasks = get_all_tasks()
    print(f"Total number of tasks: {len(tasks)}")

    duplicate_tasks = find_duplicate_tasks(tasks)
    api_calls = 0
    for idx, duplicate in enumerate(duplicate_tasks):
        print(f"Found duplicate: Task ID - {duplicate['id']}, Task name - {duplicate['name']}")
        add_possible_duplicate_tag(duplicate['id'])
        api_calls += 1
        if api_calls >= 98:
            print("Pausing due to max API calls...")
            time.sleep(65)
            api_calls = 0

    print(f"Total number of duplicate TASKS: {len(duplicate_tasks)}")


if __name__ == "__main__":
    main()
