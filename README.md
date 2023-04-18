# ClickUp
This code used the ClickUp V2 API to read through a list and find duplicate task names.
It then flags the possible duplicates with a label "possible_duplicate" against all the dupes.
Notes that our version of CU (Business) has a max API rate of 100 per minute so this needs to be run on large numbers of dupes.
The read is one API call but each write takes up one call.
The workaround would be to change the code to pause after 100 API calls or to re-run and then de-dupe 100 tasks at a time

In the secrets.py file (which is not included in this repo as it contains private keys!)
this file should contain:

api_key = 'API key from ClickUp'
team_id = ' this is your org number'
list_id1 = 'ID OF LIST 1'
list_id2 = 'ID OF LIST 2'
list_id3 = 'ID OF LIST 3'