# ClickUp
This code used the ClickUp V2 API to read through a list and find duplicate task names.
It then flags the possible duplicates with a label "possible_duplicate" against all the dupes.
Notes that our version of CU (Business) has a max API rate of 100 per minute so this needs to be run on large numbers of dupes.
The read is one API call but each write takes up one call.
