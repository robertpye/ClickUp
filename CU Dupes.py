from secrets import api_key, team_id, list_id
import requests

def get_filtered_tasks(team_id):
    url = f'https://api.clickup.com/api/v2/team/{team_id}/task'
    headers = {
        'Authorization': api_key
    }
    params = {
        'list_ids[]': list_id,
        'page': 0
    }
    all_tasks = []
    
    while True:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            raise Exception(f'Error fetching tasks: {response.text}')
        
        tasks = response.json().get('tasks', [])
        all_tasks.extend(tasks)
        
        if len(tasks) < 100:
            break
        
        params['page'] += 1
    
    return all_tasks

def find_duplicate_tasks(tasks):
    task_titles = {}
    duplicate_tasks = []
    
    for task in tasks:
        if task['name'] in task_titles:
            duplicate_tasks.append(task)
            duplicate_tasks.extend(task_titles[task['name']])
            task_titles[task['name']].append(task)
        else:
            task_titles[task['name']] = [task]
    
    return duplicate_tasks

def add_tag_to_task(task_id, task_name, tag_name):
    url = f'https://api.clickup.com/api/v2/task/{task_id}/tag/{tag_name}'
    headers = {
        'Authorization': api_key,
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f'Error adding tag to task: {response.text}')
    
    print(f'Added "{tag_name}" tag to task "{task_name}" with ID {task_id}')

if __name__ == '__main__':
    tasks = get_filtered_tasks(team_id)
    print(f'Total number of tasks: {len(tasks)}')
    
    duplicate_tasks = find_duplicate_tasks(tasks)
    print(f'Number of duplicate tasks: {len(duplicate_tasks)}')
    
    unique_duplicate_tasks = {task['id']: task for task in duplicate_tasks}.values()
    for task in unique_duplicate_tasks:
        add_tag_to_task(task['id'], task['name'], 'possible_duplicate')
