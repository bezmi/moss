#!/usr/bin/env python

from bs4 import BeautifulSoup
from pyvis.network import Network
import sys
from matplotlib import colormaps, colors
import argparse
import os
import webbrowser
import hashlib


# DEPENDENCIES:
# pip install bs4 pyvis matplotlib

# USAGE:
# python moss_nodes.py --help

# this fill will generate a html file to display a
# force-directed network graph of the MOSS report.
# First, you must have run 'submit_to_moss.py' and have a downloaded report.
# set report to the location of this report,
# output to the name of the generated network graph html,
# and min_similarity, min_lines_matched to the minimum similarity.
# nodes with matches below these values will not be included in the graph.

# to view, open the generated html file in a web browser.

# some consts
CMAP = "Spectral_r"

# the width and color of the nodes will be scaled within this range
MIN_STRENGTH_SCALE = 0.0
MAX_STRENGTH_SCALE = 100.0


def parse_moss_report(html_content, anonymize_names=False):
    soup = BeautifulSoup(html_content, "html.parser")
    rows = soup.find_all("tr")[1:]  # Skip the header row

    edges = []
    node_strength = {}

    for row in rows:
        columns = row.find_all("td")
        if len(columns) >= 3:  # Ensure row has enough columns
            file1 = columns[0].text.strip()
            file2 = columns[1].text.strip()
            lines_matched = int(columns[2].text.strip())
            # Extract similarity percentage from file name
            sim_percentage1 = int(file1.split("(")[-1].replace("%)", "").strip())
            sim_percentage2 = int(file2.split("(")[-1].replace("%)", "").strip())

            fn1 = file1.split(" ")[0].split("/")[-2]
            fn2 = file2.split(" ")[0].split("/")[-2]
            if anonymize_names:
                fn1 = str(hashlib.sha256(fn1.encode("utf-8")).hexdigest()[:6])
                fn2 = str(hashlib.sha256(fn2.encode("utf-8")).hexdigest()[:6])

            edges.append((fn1, fn2, sim_percentage1, sim_percentage2, lines_matched))

            mean_sim = (sim_percentage1 + sim_percentage2) / 2.0

            # Update node strength based on similarity
            node_strength[fn1] = node_strength.get(fn1, 0.0) + mean_sim
            node_strength[fn2] = node_strength.get(fn2, 0.0) + mean_sim

    return edges, node_strength


def create_graph(edges, node_strength, min_similarity=10, min_lines_matched=50):
    net = Network(
        # notebook=True,
        directed=True,
        height="750px",
        width="100%",
        bgcolor="#ffffff",
        font_color="#000000",
    )
    net.barnes_hut(
        # gravity=-18000,
        central_gravity=5,
        # spring_length=200,
        spring_strength=0.1,
        damping=0.5,
        overlap=1.0,
    )

    # Normalize the node size based on the maximum strength
    # max_strength = max(node_strength.values())
    max_strength = MAX_STRENGTH_SCALE
    min_strength = MIN_STRENGTH_SCALE

    for file1, file2, similarity1, similarity2, ln in edges:
        sim = (similarity1 + similarity2) / 2.0
        if (
            similarity1 > min_similarity or similarity2 > min_similarity
        ) and ln > min_lines_matched:  # Only add edges with non-zero similarity
            # a property that determines the 'size' of the edge (width and color)
            size1 = (similarity1 - min_strength) / (max_strength - min_strength)
            size2 = (similarity2 - min_strength) / (max_strength - min_strength)

            # how much to scale the size when setting edge width
            width_scale = 5.0

            cmap = colormaps[CMAP]  # You can choose any colormap
            net.add_node(
                file1,
                title=file1,
                label=f'{" ".join(file1.split("_"))}',
            )
            net.add_node(
                file2,
                title=file2,
                label=f'{" ".join(file2.split("_"))}',
            )

            net.add_edge(
                file1,
                file2,
                width=size1 * width_scale,
                label=f"{similarity1}%",
                color=colors.to_hex(cmap(size1)),
            )
            net.add_edge(
                file2,
                file1,
                width=size2 * width_scale,
                label=f"{similarity2}%",
                color=colors.to_hex(cmap(size2)),
            )

    return net


# Load the MOSS report from an HTML file
def load_moss_report(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def main():
    parser = argparse.ArgumentParser(
        description="Generate a force-directed network graph from MOSS report.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-r",
        "--report",
        type=str,
        default="./moss_report/index.html",
        help="Path to the MOSS report index.html file.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="./moss_network.html",
        help="Name of the output HTML file for the network graph.",
    )
    parser.add_argument(
        "-s",
        "--min-similarity",
        type=int,
        default=25,
        help="Minimum similarity percentage for nodes",
    )
    parser.add_argument(
        "-l",
        "--min-lines-matched",
        type=int,
        default=20,
        help="Minimum lines matched for edges",
    )

    parser.add_argument(
        "-z",
        "--anonymize-names",
        default=False,
        action="store_true",
        help="If set, anonymize the student/submission names in the graph.",
    )

    parser.add_argument(
        "-b",
        "--show-buttons",
        action="store_true",
        default=False,
        help="Show control buttons when viewing the graph in your browser.",
    )

    parser.add_argument(
        "--open-browser",
        action="store_true",
        default=False,
        help="If set, open the generated network in web browser.",
    )

    parser.add_argument(
        "-f",
        "--force",
        default=False,
        action="store_true",
        help="Overwrite the output file if it already exists.",
    )

    args = parser.parse_args()

    if args.report is None:
        args.report = "./moss_report/index.html"

    if not os.path.isfile(args.report):
        print(
            f"No MOSS report found at {args.report}. Specify a valid path to index.html using the --report flag."
        )
        sys.exit(1)
    if os.path.isfile(args.output) and not args.force:
        print(
            f"The file {args.output} already exists. Specify a different output file name using --output, or use the --force flag to overwrite it."
        )
        sys.exit(1)

    # Load MOSS report and create graph
    html_content = load_moss_report(args.report)
    edges, node_strength = parse_moss_report(html_content, args.anonymize_names)

    print(
        f"creating graph with min_similarity={args.min_similarity} and min_lines_matched={args.min_lines_matched}"
    )

    net = create_graph(
        edges, node_strength, args.min_similarity, args.min_lines_matched
    )

    if args.show_buttons:
        net.show_buttons()

    # Save and visualize the network
    net.save_graph(args.output)
    print(f"Interactive graph saved to: {args.output}")

    if args.open_browser:
        print("Opening the generated network in web browser...")
        webbrowser.open_new_tab(args.output)


# Entry point for the script
if __name__ == "__main__":
    main()
