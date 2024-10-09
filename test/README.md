I generated permutations of the test files by giving chatgpt the file and asking "I want you to generate five variations of the preceding code that achieves exactly the same purpose, with different levels of similarity to it such that I can use your examples as test cases for a code similarity checking software".

It works reasonably well for testing.

`MOSS_USERID=123456 run_test.sh` to test the `check_similarity.sh` script. Make sure that `MOSS_USERID` is valid.

If your browser doesn't open, then manually open `moss_report/index.html` to view the report and `./moss_network.html` for the graph.
