"""
Copyright (c) 2022 Nordic Semiconductor ASA

This script is only inteded to be run by GitHub actions as a CRON job.
It uses the GitHub API to retrieve a list of collaborators for a given
repository. 
"""

import requests
import argparse
import re
from pathlib import Path

URL_TEMPLATE = "https://api.github.com/repos/{}/collaborators?per_page=100"

HEADERS_TEMPLATE = {
    "Accept": "application/vnd.github+json",
    "Authorization": "Bearer {}",
    "X-GitHub-Api-Version": "2022-11-28",
}


def main(url: str, headers: dict, output_file: Path = None) -> None:
    all_ids = []

    while url:
        response = requests.get(url, headers=headers)
        ids = [f"{o['id']}-github" for o in response.json()]
        all_ids += ids

        # Get link to next page of collaborators
        url = None
        if "Link" in response.headers:
            links = response.headers["Link"].split(",")
            for link in links:
                m = re.match(r'\<(.*)\>;\s*rel="(.*)"', link.strip())
                link_url, rel = m.groups()
                if rel == "next":
                    url = link_url
                    break

    if output_file:
        with open(output_file, "w") as f:
            f.writelines([id + "\n" for id in all_ids])
    else:
        print(all_ids)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-o",
        "--output-file",
        type=Path,
        default=None,
        help="If not None, save results to the specified local file.",
    )

    parser.add_argument(
        "-t",
        "--token",
        type=str,
        required=True,
        help="Authorization bearer token for the GitHub API.",
    )

    parser.add_argument(
        "-r",
        "--repository",
        type=str,
        required=True,
        help="repository name on the form 'OWNER/REPO'.",
    )

    args = parser.parse_args()

    url = URL_TEMPLATE.format(args.repository)

    headers = HEADERS_TEMPLATE
    headers["Authorization"] = f"Bearer {args.token}"

    main(url, headers, args.output_file)
