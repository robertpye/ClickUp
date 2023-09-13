import requests
from typing import List, Dict
from datetime import datetime
import time
from secrets import api_key, team_id, view_active_partners

# headers
headers = {"Authorization": api_key}

# Variables for the target string in comments and tag name
target_string = "For the last 22 weeks we have been publishing"
tag_name = "podcast email"
start_date = "01/06/23"  # your date string here

# convert the string to datetime object
start_date = datetime.strptime(start_date, "%d/%m/%y")

# convert the datetime object to Unix time
start_date_unix = int(time.mktime(start_date.timetuple())) * 1000  # multiply by 1000 to convert to milliseconds

# function to get all tasks from a view
def get_tasks_from_view(view_id: str) -> List[Dict]:
    all_tasks = []
    page = 0
    while True:
        url = f"https://api.clickup.com/api/v2/view/{view_id}/task?page={page}"
        response = requests.get(url, headers=headers)
        response_json = response.json()
        tasks = response_json["tasks"]
        if not tasks:
            break
        all_tasks.extend(tasks)
        page += 1
    print(f"Total number of tasks from the view: {len(all_tasks)}")
    return all_tasks

# function to get comments of a task
def get_comments(task_id):
    url = f"https://api.clickup.com/api/v2/task/{task_id}/comment"
    query = {
      "custom_task_ids": "true",
      "team_id": team_id,
      "start": start_date_unix,
      "start_id": "string"
    }
    response = requests.get(url, headers=headers, params=query)
    response_json = response.json()
    if 'comments' in response_json:
        return response_json["comments"]
    else:
        print(f"No comments found for task {task_id}.")
        return []



# function to add a tag to a task
def set_tag_on_task(task_id: str, tag_name: str):
    url = f"https://api.clickup.com/api/v2/task/{task_id}/tag/{tag_name}"
    response = requests.post(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to add tag to task {task_id}. Response: {response.text}")
    else:
        print(f"Tag '{tag_name}' successfully added to task {task_id}.")



def main():
    tasks = get_tasks_from_view(view_active_partners)
    for task in tasks:
        print(f"Getting comments for task: Task ID - {task['id']}, Task name - {task['name']}")
        comments = get_comments(task["id"])
        for comment in comments:
            if 'comment' in comment:
                comment_text = ''.join([text_block['text'] for text_block in comment['comment'] if 'text' in text_block])
                if target_string in comment_text:
                    print(f"Target string found in task {task['id']}. Setting tag...")
                    set_tag_on_task(task['id'], tag_name)
                else:
                    print(f"No match found in task {task['id']}.")
            else:
                print(f"Comment field not found in task {task['id']}.")

if __name__ == "__main__":
    main()