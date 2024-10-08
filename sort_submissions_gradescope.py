#!/usr/bin/env python3

import os
from datetime import datetime, timedelta, timezone
import glob
import csv
from dataclasses import dataclass
import shutil
import argparse

##################
### QUICKSTART ###
##################
# This program processes submission metadata for a Gradescope online assignment.
# python3 sort_submissions_gradescope.py --due-date "2024-10-01 16:00:00 +1000".

# Processed metadata (including overdue time) is saved to args.processed_csv_path.
# Code files are copied to args.processed_dir_path, where each directory is named based
# on the names of the submitters, for using with MOSS in dir_mode.

# for usage help:
# python3 sort_submissions_gradescope.py --help


##################
### PARAMETERS ###
##################
@dataclass
class Submission:
    id: str
    names: list[str]
    student_ids: list[str]
    submitted_datetime: datetime
    code_files: list[str]
    pdf_files: list[str]
    overdue_hrs: float


def process_submissions(
    due_date: str,
    metadata_path: str,
    processed_csv_path: str,
    processed_dir_path: str,
    assignment_files_directory: str,
    code_file_match_pattern: str,
    pdf_file_match_pattern: str,
    overdue_leniency: timedelta,
) -> None:
    _datetime_format = "%Y-%m-%d %H:%M:%S %z"

    # Convert due date string to datetime
    due_datetime = datetime.strptime(due_date, _datetime_format)
    tz_local = due_datetime.tzinfo
    due_datetime = due_datetime.astimezone(tz_local)

    submissions: dict[str, Submission] = {}

    # Read and process submission_metadata.csv
    with open(metadata_path, "r") as metadata_csv:
        metadata_reader = csv.DictReader(metadata_csv)
        for row in metadata_reader:
            if row["Status"] != "Missing":
                submission_id = row["Submission ID"]
                student_name = row["First Name"] + " " + row["Last Name"]
                student_id = row["Student ID"]

                if submission_id in submissions:
                    print(
                        f"Adding {student_name} to existing submission: {submission_id}"
                    )
                    submissions[submission_id].names.append(student_name)
                    submissions[submission_id].student_ids.append(student_id)
                    continue

                print(f"Adding new submission for student {student_name}")
                submission_datetime: datetime = datetime.strptime(
                    row["Question 1 Submitted At"], _datetime_format
                ).astimezone(tz_local)
                filepath = os.path.join(
                    assignment_files_directory, f"submission_{submission_id}"
                )
                codefiles = glob.glob(os.path.join(filepath, code_file_match_pattern))
                pdf_files = glob.glob(os.path.join(filepath, pdf_file_match_pattern))
                overdue_hrs = 0
                if (submission_datetime - due_datetime) > overdue_leniency:
                    overdue_hrs = (
                        submission_datetime - (due_datetime + overdue_leniency)
                    ) / timedelta(hours=1)
                submissions[submission_id] = Submission(
                    id=submission_id,
                    names=[student_name],
                    student_ids=[student_id],
                    submitted_datetime=submission_datetime,
                    code_files=codefiles,
                    pdf_files=pdf_files,
                    overdue_hrs=overdue_hrs,
                )

    # Write submissions to a CSV
    with open(processed_csv_path, "w") as processed_csv:
        processed_writer = csv.writer(processed_csv)
        processed_writer.writerow(
            [
                "Submission ID",
                "Student Names",
                "Student IDs",
                "Submitted Datetime",
                "Overdue Hours",
                "Code Files",
                "PDF Files",
            ]
        )
        for submission in submissions.values():
            processed_writer.writerow(
                [
                    submission.id,
                    ",".join(submission.names),
                    ",".join(submission.student_ids),
                    submission.submitted_datetime.strftime("%Y-%m-%d %H:%M:%S %z"),
                    submission.overdue_hrs,
                    ",".join(submission.code_files),
                    ",".join(submission.pdf_files),
                ]
            )

    os.makedirs(processed_dir_path, exist_ok=False)
    for submission in submissions.keys():
        dirname = "-".join(
            ["_".join(name.split(" ")) for name in submissions[submission].names]
        )
        for codefile in submissions[submission].code_files:
            if not os.path.exists(f"{processed_dir_path}/{dirname}"):
                os.makedirs(f"{processed_dir_path}/{dirname}")
            shutil.copy2(
                codefile, f"{processed_dir_path}/{dirname}/{os.path.basename(codefile)}"
            )


def main():
    parser = argparse.ArgumentParser(
        description="Process Gradescope assignment submissions.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-d",
        "--due-date",
        type=str,
        required=True,
        help="Due date in format YYYY-MM-DD HH:MM:SS z, where z is the UTC timezone, such as +1000",
    )
    parser.add_argument(
        "-m",
        "--metadata-path",
        type=str,
        default="submission_metadata.csv",
        help="Path to the submission metadata csv file.",
    )
    parser.add_argument(
        "-p",
        "--processed-csv-path",
        type=str,
        default="submissions_processed.csv",
        help="Path to save the processed submissions CSV.",
    )
    parser.add_argument(
        "-o",
        "--processed-dir-path",
        type=str,
        default="./sorted",
        help="Directory to write processed submissions.",
    )
    parser.add_argument(
        "-i",
        "--assignment-files-directory",
        type=str,
        default="./",
        help="Directory containing assignment files.",
    )

    parser.add_argument(
        "-l",
        "--overdue-leniency",
        type=float,
        default=1.0,
        help="Assignments submitted within this many hours of the due datetime are not considered late.",
    )

    parser.add_argument(
        "--code-file-match-pattern",
        type=str,
        default="*.py",
        help="Glob pattern to match code files.",
    )

    parser.add_argument(
        "--pdf-file-match-pattern",
        type=str,
        default="*.pdf",
        help="Glob pattern to match pdf files.",
    )

    args = parser.parse_args()

    overdue_leniency = timedelta(hours=args.overdue_leniency)
    print(overdue_leniency)

    process_submissions(
        args.due_date,
        args.metadata_path,
        args.processed_csv_path,
        args.processed_dir_path,
        args.assignment_files_directory,
        args.code_file_match_pattern,
        args.pdf_file_match_pattern,
        overdue_leniency,
    )


if __name__ == "__main__":
    main()
