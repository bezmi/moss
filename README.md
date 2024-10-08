# Usage
**`sort_submissions_gradescope.py`:** processes the extracted submissions for a gradescope 'online assignment'
and outputs a processed csv file that contains the columns:
```
Submission ID,Student Names,Student IDs,Submitted Datetime,Overdue Hours,Code Files,PDF Files
```

**`submit_to_moss.py`:** takes the processed files from `sort_submissions_gradescope.py` and sends them to MOSS to generate and download a similarity report.

**`moss_nodes.py`:**  generates a directed network graph of the submissions to visualise groups of similar ones.
An example graph with anonymized names is below.
Edges are labeled and coloured with similarity percentage. Nodes are labeled with the names of the submitters.

![an example graph generated using moss_nodes.py](./example_graph.png)

**`check_similarity.sh`:** contains a basic workflow that runs the programs above in succession given DUE_DATE in the format 'YYYY-MM-DD HH:MM:SS z',
where z is the UTC timezone such as '+1000'.
Running this file once will create the virtual env 'moss_env' within the root directory of this repo.

Run each python file with the "--help" argument to see usage help.

There are comments at the start of each file with (maybe) more details.

