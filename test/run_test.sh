#!/usr/bin/env bash

rm moss_report lib sorted moss_network.html submissions_processed.csv -r

../check_similarity.sh "2024-10-02 10:00:00 +1000"
