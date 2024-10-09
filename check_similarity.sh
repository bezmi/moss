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
# set USERID here to a valid MOSS user id, or use the MOSS_USERID environment variable.
# to generate one, send an email to:
#     moss@moss.stanford.edu
# where the body of the message is exactly:
#   registeruser
#   mail username@domain
# where username@domain is your email address
# you will shortly receive an email to that address with a bash script in the body
# search for "userid" in this email. Input the value here.

# If the MOSS_USERID environment variable is not set, then script will error out
USERID=${MOSS_USERID:-""}

if [ -z "$USERID" ]; then
  echo "USERID not valid. Please set it in check_similarity.sh, or use the MOSS_USERID environment variable."
  echo ""
  echo "usage: check_similarity.sh <due_date>"
  echo "date format: 'YYYY-MM-DD HH:MM:SS Z', where Z is the UTC timezone such as +1000."
  exit 1
fi

if [ "${FORCE}" = "TRUE" ]; then
  echo "FORCE flag is set."
  FORCE_FLAG="--force"
fi

# set DUE_DATE to the correct value. OPEN_BROWSER will open the network graph and MOSS report in a
# browser tab if set to 'TRUE'.
if [ -z "$1" ]; then
  echo "Due date is required!"
  echo ""
  echo "usage: check_similarity.sh <due_date>"
  echo "date format: 'YYYY-MM-DD HH:MM:SS Z', where Z is the UTC timezone such as +1000."
  exit 1
else
  DUE_DATE="$1"
fi

if [ ! -z "${BASE_FILES}" ]; then
  BASE_FILES_FLAG="--base-files ${BASE_FILES}"
fi

# Change these values as needed.
MIN_LINES=10
MIN_SIMILARITY=25

# opens the browser automatically to show MOSS report and node graph.
OPEN_BROWSER="TRUE"

if [ "$OPEN_BROWSER" = "TRUE" ]; then
  BROWSER_FLAG="--open-browser"
fi

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

python3 ${_SCRIPT_DIR}/sort_submissions_gradescope.py -d "${DUE_DATE}" ${FORCE_FLAG}
status=$?
if [ $status -ne 0 ]; then
  echo "Sorting submissions failed. Exiting."
  exit 1
fi

REPORT_GEN_OUTPUT="$(python3 ${_SCRIPT_DIR}/submit_to_moss.py --userid ${USERID} ${BROWSER_FLAG} ${BASE_FILES_FLAG})"

status=$?
if [ $status -eq 0 ]; then
  echo "${REPORT_GEN_OUTPUT}"
  echo MOSS report created successfully at $(echo "${REPORT_GEN_OUTPUT}" | tail -n 1).
  report="--report $(echo "${REPORT_GEN_OUTPUT}" | tail -n 1)"
else
  echo "${REPORT_GEN_OUTPUT}"
  echo "Creating MOSS report failed. Exiting."
  exit 1
fi

python3 ${_SCRIPT_DIR}/moss_nodes.py $report --min-similarity $MIN_SIMILARITY --min-lines-matched $MIN_LINES $BROWSER_FLAG $FORCE_FLAG

# deactive venv
deactivate



