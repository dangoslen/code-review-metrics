#!/usr/bin/env python3

from dateutil.parser import parse
import argparse
import requests

import csv

query = """query {{
  search(query: \"is:merged is:pr repo:{}\", type: ISSUE, last: 100) {{
    issueCount
    edges {{
      node {{
        ... on PullRequest {{
        number
        title
        repository {{
          nameWithOwner
        }}
        comments {{
          totalCount
        }}
        reviews(first: 1) {{
          edges {{
            node {{
              ... on PullRequestReview {{
                reviewedAt: publishedAt
                reviewedBy: author {{
                  login
                }}
              }}
            }}
          }}
        }}
        createdAt
        createdBy: author {{
            login
        }}
        mergedAt
        url
        changedFiles
        additions
        deletions
        }}
      }}
    }}
  }}
}}
"""
 
def fetch_code_review_metrics(repo, token):
    url = 'https://api.github.com/graphql'
    formatted_query = query.format(repo)
    auth = 'Bearer {}'.format(token)
    headers = {
        'Authorization': auth    
    }
    response = requests.post(url=url, json={'query': formatted_query}, headers=headers)
    return response

def parse_into_dicts(body):
    prs = body["data"]["search"]["edges"]
    return map(parse_pr_into_dict, prs)

def parse_pr_into_dict(pr):
    node = pr["node"]
    created_at = node["createdAt"]
    merged_at = node["mergedAt"]
    cycle_time = time_difference_in_minutes(created_at, merged_at)
    lines_changed = node["additions"] + node["deletions"]
    pr_dict = {
        'title': node["title"],
        'number': node["number"],
        'created_by': node["createdBy"]["login"],
        'created_at': node["createdAt"],
        'merged_at': node["mergedAt"],
        'url':  node["url"],
        'cycle_time_minutes': cycle_time,
        'first_reviewed_at': '-',
        'first_reviewed_by': '-',
        'lead_time_minutes': 0,
        'lines_changed': lines_changed,
        'comments_added': node["comments"]["totalCount"]
    }

    reviews = node["reviews"]["edges"]
    if len(reviews) > 0:
        first_review = reviews[0]['node']
        reviewed_at = first_review['reviewedAt']
        lead_time = time_difference_in_minutes(created_at, reviewed_at)
        pr_dict['first_reviewed_at'] = reviewed_at
        pr_dict['first_reviewed_by'] = first_review['reviewedBy']['login']
        pr_dict['lead_time_minutes'] = lead_time

    return pr_dict


def time_difference_in_minutes(start_ts, end_ts):
    end = parse(end_ts)
    start = parse(start_ts)
    return (end - start).total_seconds() / 60

def print_as_csv(prs):
    with open('code_review_metrics.csv', 'w', newline='') as csvfile:

        field_names = [ 
            'title', 'number', 'url', 'created_by', 'created_at', 'first_reviewed_at', 'first_reviewed_by', 'merged_at',
            'cycle_time_minutes', 'lead_time_minutes', 'lines_changed', 'comments_added'
        ]

        writer = csv.DictWriter(csvfile, fieldnames=field_names)

        writer.writeheader()
        for pr in prs:
            writer.writerow(pr)


def main():
    # Initialize parser
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-r", "--repo", help = "The repository to grab pull request metrics from")
    parser.add_argument("-t", "--token", help = "A GitHub token to access the GitHub API")
    parser.add_argument("-f", "--file", help = "The path to the csv file to generate")
    parser.add_argument("-g", "---build-graph", action=argparse.BooleanOptionalAction, help = "Build the graph")

    # Read arguments from command line
    args = parser.parse_args()

    response = fetch_code_review_metrics(args.repo, args.token)
    if response.status_code == 200:
        prs = parse_into_dicts(response.json())
        print_as_csv(prs)


if __name__ == "__main__":
    main()