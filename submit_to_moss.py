#!/usr/bin/env python3

# generally you should run 'sort_submissions_gradescope.py' first to generate a 'sorted' folder
# and then run this file without any args.

# for usage:
# python3 submit_to_moss.py --help

# Shahzeb Imran 2023-Nov-01

# this script will send either a directory, or a single file
# MOSS for plagiarism detection.

import os
import glob
import socket
from urllib.request import urlopen
from threading import Thread
import logging
import re
import argparse
import webbrowser
import sys

# this is the userid generated by me.
# if it stops working, send an email to:
#     moss@moss.stanford.edu
# where the body of the message is exactly:
#   registeruser
#   mail username@domain
# where username@domain is your email address
# you will shortly receive an email to that address with a bash script in the body
# search for "userid" in this email. Input the value here.
USERID = ""

# original files can be found at: https://github.com/soachishti/moss.py
# I've just pasted the functions below to make it easier to store on blackboard

# MIT License
#
# Copyright (c) 2017 Syed Owais Ali Chishti
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


class Moss:
    languages = (
        "c",
        "cc",
        "java",
        "ml",
        "pascal",
        "ada",
        "lisp",
        "scheme",
        "haskell",
        "fortran",
        "ascii",
        "vhdl",
        "verilog",
        "perl",
        "matlab",
        "python",
        "mips",
        "prolog",
        "spice",
        "vb",
        "csharp",
        "modula2",
        "a8086",
        "javascript",
        "plsql",
    )
    server = "moss.stanford.edu"
    port = 7690

    def __init__(self, user_id, language="c"):
        self.user_id = user_id
        self.options = {"l": "c", "m": 10, "d": 0, "x": 0, "c": "", "n": 250}
        self.base_files = []
        self.files = []

        if language in self.languages:
            self.options["l"] = language

    def setIgnoreLimit(self, limit):
        self.options["m"] = limit

    def setCommentString(self, comment):
        self.options["c"] = comment

    def setNumberOfMatchingFiles(self, n):
        if n > 1:
            self.options["n"] = n

    def setDirectoryMode(self, mode):
        self.options["d"] = mode

    def setExperimentalServer(self, opt):
        self.options["x"] = opt

    def addBaseFile(self, file_path, display_name=None):
        if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
            self.base_files.append((file_path, display_name))
        else:
            raise Exception(
                "addBaseFile({}) => File not found or is empty.".format(file_path)
            )

    def addFile(self, file_path, display_name=None):
        if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
            self.files.append((file_path, display_name))
        else:
            raise Exception(
                "addFile({}) => File not found or is empty.".format(file_path)
            )

    def addFilesByWildcard(self, wildcard):
        for file in glob.glob(wildcard, recursive=True):
            self.files.append((file, None))

    def getLanguages(self):
        return self.languages

    def uploadFile(self, s, file_path, display_name, file_id, on_send):
        if display_name is None:
            # If no display name added by user, default to file path
            # Display name cannot accept \, replacing it with /
            display_name = file_path.replace(" ", "_").replace("\\", "/")

        size = os.path.getsize(file_path)
        message = "file {0} {1} {2} {3}\n".format(
            file_id, self.options["l"], size, display_name
        )
        s.send(message.encode())
        with open(file_path, "rb") as f:
            s.send(f.read(size))
        on_send(file_path, display_name)

    def send(self, on_send=lambda file_path, display_name: None):
        s = socket.socket()
        s.connect((self.server, self.port))

        s.send("moss {}\n".format(self.user_id).encode())
        s.send("directory {}\n".format(self.options["d"]).encode())
        s.send("X {}\n".format(self.options["x"]).encode())
        s.send("maxmatches {}\n".format(self.options["m"]).encode())
        s.send("show {}\n".format(self.options["n"]).encode())

        s.send("language {}\n".format(self.options["l"]).encode())
        recv = s.recv(1024)
        if recv == "no":
            s.send(b"end\n")
            s.close()
            raise Exception("send() => Language not accepted by server")

        for file_path, display_name in self.base_files:
            self.uploadFile(s, file_path, display_name, 0, on_send)

        index = 1
        for file_path, display_name in self.files:
            self.uploadFile(s, file_path, display_name, index, on_send)
            index += 1

        s.send("query 0 {}\n".format(self.options["c"]).encode())

        response = s.recv(1024)

        s.send(b"end\n")
        s.close()

        return response.decode().replace("\n", "")

    def saveWebPage(self, url, path):
        if len(url) == 0:
            raise Exception("Empty url supplied")

        response = urlopen(url)
        charset = response.headers.get_content_charset()
        content = response.read().decode(charset)

        f = open(path, "w", encoding="utf-8")
        f.write(content)
        f.close()


def process_url(url, urls, base_url, path, on_read):
    from bs4 import (
        BeautifulSoup,
    )  # Backward compability, don't break Moss when bs4 not available.

    logging.debug("Processing URL: " + url)
    response = urlopen(url)
    html = response.read()
    on_read(url)
    soup = BeautifulSoup(html, "lxml")
    file_name = os.path.basename(url)

    if (
        not file_name or len(file_name.split(".")) == 1
    ):  # Not file name eg. 123456789 or is None
        file_name = "index.html"

    for more_url in soup.find_all(["a", "frame"]):
        if more_url.has_attr("href"):
            link = more_url.get("href")
        else:
            link = more_url.get("src")

        if link and (link.find("match") != -1):  # Download only results urls
            link_fragments = link.split("#")
            link = link_fragments[0]  # remove fragment from url

            link_hash = ""
            if len(link_fragments) > 1:
                link_hash = "#" + link_fragments[1]

            basename = os.path.basename(link)

            if basename == link:  # Handling relative urls
                link = base_url + basename

            if more_url.name == "a":
                more_url["href"] = basename + link_hash
            elif more_url.name == "frame":
                more_url["src"] = basename

            if link not in urls:
                urls.append(link)

    f = open(os.path.join(path, file_name), "wb")
    f.write(soup.encode(soup.original_encoding))
    f.close()


def download_report(
    url, path, connections=4, log_level=logging.DEBUG, on_read=lambda url: None
):
    logging.basicConfig(level=log_level)

    if len(url) == 0:
        raise Exception("Empty url supplied")

    output_dir = make_dir(path)
    print(f"The MOSS report will now be downloaded into {output_dir}")

    base_url = url + "/"
    urls = [url]
    threads = []

    logging.debug("=" * 80)
    logging.debug("Downloading Moss Report - URL: " + url)
    logging.debug("=" * 80)

    # Handling thread
    for url in urls:
        t = Thread(target=process_url, args=[url, urls, base_url, output_dir, on_read])
        t.start()
        threads.append(t)

        if len(threads) == connections or len(urls) < connections:
            for thread in threads:
                thread.join()
                threads.remove(thread)
                break

    logging.debug("Waiting for all threads to complete")
    for thread in threads:
        thread.join()
    return f"{output_dir}/index.html"


# end moss.py, the rest is my code


def make_dir(output_dir_name):
    output_dir = output_dir_name
    i = 0
    while True:
        try:
            if i == 0:
                os.makedirs(output_dir, exist_ok=False)
            else:
                output_dir = f"{output_dir_name}.{i}"
                os.makedirs(output_dir, exist_ok=False)
        except FileExistsError:
            if i > 10:
                print(
                    f"Failed to create directory {output_dir_name}. Too many attempts."
                )
                sys.exit(1)
            print(
                f"WARNING: {output_dir} already exists. Trying {output_dir_name}.{i+1}"
            )
            i += 1

        else:
            break

    return output_dir


def main():
    parser = argparse.ArgumentParser(
        description="Submit files to MOSS for plagiarism detection. The final line of output will be path to the index.html file of the downloaded report.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-i",
        "--submissions-dir",
        type=str,
        default="./sorted",
        help="Directory where student submissions are stored.",
    )

    parser.add_argument(
        "-o",
        "--report-output-dir",
        type=str,
        default="./moss_report",
        help="Directory where MOSS report will be stored.",
    )
    parser.add_argument(
        "-p",
        "--file-pattern",
        type=str,
        default=r"((task[-_ ]?5\.py)|(T5[-_ ]?(\w+)?|(\w+)[-_ ]?T5)\.py)",
        help="Regex pattern to match specific files for sending when dir_mode=False.",
    )
    parser.add_argument(
        "-b",
        "--base-files",
        nargs="*",
        type=str,
        default=[],
        help="List of base files that should be ignored in the comparison.",
    )

    parser.add_argument("--userid", type=int, required=False, help="User ID for MOSS.")
    parser.add_argument(
        "-l",
        "--language",
        type=str,
        default="python",
        choices=[
            "c",
            "cc",
            "java",
            "ml",
            "pascal",
            "ada",
            "lisp",
            "scheme",
            "haskell",
            "fortran",
            "ascii",
            "vhdl",
            "verilog",
            "perl",
            "matlab",
            "python",
            "mips",
            "prolog",
            "spice",
            "vb",
            "csharp",
            "modula2",
            "a8086",
            "javascript",
            "plsql",
        ],
        help="Programming language of the submissions.",
    )
    parser.add_argument(
        "--no-dir-mode",
        action="store_true",
        help="Disable directory mode. Directory mode treats all files in a directory as a single submission, disabling it will send them individually.",
    )

    parser.add_argument(
        "--open-browser",
        action="store_true",
        default=False,
        help="If set, open the MOSS report in a browser after downloading.",
    )

    args = parser.parse_args()

    submissions_dir = args.submissions_dir
    report_output_dir = args.report_output_dir
    file_pattern = args.file_pattern

    userid = args.userid
    if not args.userid:
        if USERID is not None:
            userid = USERID
        else:
            print("User ID for MOSS is required.")
            sys.exit(1)

    language = args.language

    dir_mode = True
    if args.no_dir_mode:
        dir_mode = False

    base_files = args.base_files

    students = os.listdir(submissions_dir)
    moss_files_to_submit = []

    for student in students:
        student_dir = os.path.join(submissions_dir, student)
        files = glob.glob(f"{student_dir}/*")
        if len(files) == 0:
            print(f"submission: {student} has no files, skipping.")
            continue

        file_found = False
        for file in files:
            if dir_mode:
                moss_files_to_submit.append(file)
                continue
            if len(file_pattern) != 0:
                if re.search(file_pattern, file, re.IGNORECASE) is not None:
                    moss_files_to_submit.append(file)
                    file_found = True
                    break
            else:
                print("dir_mode not set and file_pattern empty!")
                sys.exit(1)
        if not file_found and not dir_mode:
            if len(files) == 1:
                moss_files_to_submit.append(files[0])
                continue
            print("File not found for student: ", student, len(files))
            for i in range(len(files)):
                print(f"{i}: {os.path.basename(files[i])}")

            try:
                idx = int(
                    input("Enter the index of the file to submit, or return to skip: ")
                )
            except ValueError:
                continue

            moss_files_to_submit.append(files[idx])

    try:
        m = Moss(userid, language)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    try:
        if dir_mode:
            print("Setting directory mode and sending all files")
            m.setDirectoryMode(1)

        # use the line below to specify a "base file" that will be ignored in the comparison
        # this should be used to include code that all students will have in their submission,
        # eg, if you provided a template.

        for file in base_files:
            m.addBaseFile(file)

        # add the concatenated files
        n_files = len(moss_files_to_submit)
        files_sent = []

        for f in moss_files_to_submit:
            m.addFile(f)

        def progress_func(file_path, display_name):
            files_sent.append(file_path)
            print(f"sending file {len(files_sent)} of {n_files}\n", end="", flush=True)

        url = m.send(
            # lambda file_path, display_name: print(f"sending {file_path}\n", end="", flush=True)
            progress_func
        )
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    if not url:
        print("The returned MOSS url is empty. Did you provide a valid userid?")
        sys.exit(1)

    print()

    # you can visit this URL straight away but it will be deleted after 14 days
    print()
    print(
        "NOTE: The MOSS url is below. You can visit this URL now, but it will be deleted after 14 days."
    )
    print("Report Url: " + url)
    print()

    # download the MOSS report to the report_output_dir
    report_output = download_report(
        url,
        report_output_dir,
        connections=8,
        log_level=20,  # 10 to set to DEBUG, 20 disables logging.
        on_read=lambda url: print(f"Downloaded file: {url}\n", end="", flush=True),
    )

    print()
    print("The report download has completed.")

    if args.open_browser:
        print(f"Opening {report_output} in browser...")
        webbrowser.open(f"{report_output}")

    print(f"{report_output}")


if __name__ == "__main__":
    main()
