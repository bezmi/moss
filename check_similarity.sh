#!/usr/bin/env bash

# Use this script to process all submissions for a gradescope 'online assignment'.
# Download the submissions, extract the files, put the python files and this shell script
# in the same directory and run this script. It will sort the submissions, send them to MOSS,
# download the report, and then generate a network graph of the repport for visualising
# groups of similar submissions.
#
# It will also output 'submissions_sorted.csv', which is a file that contains details about
# the submissions, such as whether they were overdue and by how many hours.
#
# set USERID to a valid MOSS user id.
# to generate one, send an email to:
#     moss@moss.stanford.edu
# where the body of the message is exactly:
#   registeruser
#   mail username@domain
# where username@domain is your email address
# you will shortly receive an email to that address with a bash script in the body
# search for "userid" in this email. Input the value here.
USERID="12345678"


# set DUE_DATE to the correct value. OPEN_BROWSER will open the network graph and MOSS report in a
# browser tab if set to 'TRUE'.
DUE_DATE="2024-10-26 16:00:00 +1000"

# Change these values as needed.
MIN_LINES=10
MIN_SIMILARITY=25


OPEN_BROWSER="TRUE"

# the directory within which this script is located.
# venv will be created here if it does not exist.
_SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
echo $_SCRIPT_DIR

# activeate venv if it exists, otherwise create and install requirements
if [ -d "${_SCRIPT_DIR}/moss_env" ]; then
  echo "Using existing moss_env."
  source ${_SCRIPT_DIR}/moss_env/bin/activate
else
  echo "moss_env virtual environment does not exist. Creating it."
  python3 -m venv ${_SCRIPT_DIR}/moss_env
  source ${_SCRIPT_DIR}/moss_env/bin/activate
  pip install -r ${_SCRIPT_DIR}/requirements.txt
fi

python3 ${_SCRIPT_DIR}/sort_submissions_gradescope.py -d "${DUE_DATE}"
if [ $OPEN_BROWSER = "TRUE" ]; then
  python3 ${_SCRIPT_DIR}/submit_to_moss.py --userid $USERID --open-browser
  python3 ${_SCRIPT_DIR}/moss_nodes.py --min-similarity $MIN_SIMILARITY --min-lines-matched $MIN_LINES --open-browser
else
  python3 ${_SCRIPT_DIR}/submit_to_moss.py --userid $USERID
  python3 ${_SCRIPT_DIR}/moss_nodes.py --min-similarity $MIN_SIMILARITY --min-lines-matched $MIN_LINES
fi

# deactive venv
deactivate



