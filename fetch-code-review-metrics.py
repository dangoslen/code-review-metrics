#!/usr/bin/env python3

from dateutil.parser import parse
import argparse
import requests
from datetime import datetime
import csv

BASE_QUERY = """query($query: String!, $cursor: String) {
  search(query: $query, type: ISSUE, first: 100, after: $cursor) {
    issueCount
    pageInfo {
      hasNextPage
      endCursor
    }
    edges {
      node {
        ... on PullRequest {
        number
        title
        repository {
          nameWithOwner
        }
        comments {
          totalCount
        }
        reviews(first: 1) {
          edges {
            node {
              ... on PullRequestReview {
                reviewedAt: publishedAt
                reviewedBy: author {
                  login
                }
              }
            }
          }
        }
        timelineItems(itemTypes: [REVIEW_REQUESTED_EVENT], first: 1) {
          nodes {
            ... on ReviewRequestedEvent {
              createdAt
            }
          }
        }
        createdAt
        createdBy: author {
            login
        }
        mergedAt
        url
        changedFiles
        additions
        deletions
        }
      }
    }
  }
}
"""


def fetch_pull_requests(query, queryOpts, token, start_date=None):
    if query is None:
        queryString = "is:merged is:pr"

        if queryOpts["repo"] is not None:
            queryString = "{} repo:{}".format(queryString, queryOpts["repo"])

        if queryOpts["org"] is not None:
            queryString = "{} org:{}".format(queryString, queryOpts["org"])

        # Add date filter if start_date is provided
        if start_date:
            # Format date for GitHub search (YYYY-MM-DD)
            date_str = start_date.strftime("%Y-%m-%d")
            queryString = "{} created:>={}".format(queryString, date_str)

        # Use the BASE_QUERY template for default queries
        graphql_query = BASE_QUERY
        use_variables = True
    else:
        # Use the custom query directly
        graphql_query = query
        use_variables = False
        print("Warning: Custom queries don't support pagination. Consider using --repo and --start-date instead for full data retrieval.")

    all_prs = []
    cursor = None

    # Set up API request variables (these don't change)
    url = 'https://api.github.com/graphql'
    auth = 'Bearer {}'.format(token)
    headers = {
        'Authorization': auth
    }

    while True:
        if use_variables:
            variables = {
                "query": queryString,
                "cursor": cursor
            }
            request_data = {'query': graphql_query, 'variables': variables}
        else:
            # For custom queries, don't use variables
            request_data = {'query': graphql_query}

        response = requests.post(url=url, json=request_data, headers=headers)

        if response.status_code != 200:
            return response

        data = response.json()

        # Check for GraphQL errors
        if "errors" in data:
            print(f"GraphQL errors: {data['errors']}")
            return response

        search_data = data["data"]["search"]

        # Add PRs from this page
        prs = search_data["edges"]
        all_prs.extend(prs)

        # Check if there are more pages
        page_info = search_data["pageInfo"]
        if not page_info["hasNextPage"]:
            break

        cursor = page_info["endCursor"]

    return all_prs


def parse_into_dicts(prs):
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
        'url': node["url"],
        'cycle_time_minutes': cycle_time,
        'first_reviewed_at': '-',
        'first_reviewed_by': '-',
        'lead_time_minutes': 0,
        'lines_changed': lines_changed,
        'comments_added': node["comments"]["totalCount"]
    }

    reviews = node.get("reviews", {}).get("edges", [])
    if not reviews:
        return pr_dict

    first_review = reviews[0]['node']
    reviewed_at = first_review['reviewedAt']

    lead_time_start = created_at
    timeline_items = node.get("timelineItems", {}).get("nodes", [])
    if timeline_items:
        review_requested_at = timeline_items[0]['createdAt']
        if parse(reviewed_at) > parse(review_requested_at):
            lead_time_start = review_requested_at

    lead_time = time_difference_in_minutes(lead_time_start, reviewed_at)
    pr_dict['first_reviewed_at'] = reviewed_at
    pr_dict['first_reviewed_by'] = first_review['reviewedBy']['login']
    pr_dict['lead_time_minutes'] = lead_time

    return pr_dict


def time_difference_in_minutes(start_ts, end_ts):
    end = parse(end_ts)
    start = parse(start_ts)
    return (end - start).total_seconds() / 60


def print_as_csv(prs, filename):
    with open(filename, 'w', newline='') as csvfile:
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

    parser.add_argument("-o", "--org", help="The orginization to grab pull request metrics from")
    parser.add_argument("-r", "--repo", help="The repository to grab pull request metrics from")
    parser.add_argument("-q", "--query", help="The query to search for pull requests. See more at <> . This overrides whatever was set via '-r' or '--repo'")
    parser.add_argument("-t", "--token", help="A GitHub token to access the GitHub API")
    parser.add_argument("-f", "--file", help="The path to the csv file to generate")
    parser.add_argument("-s", "--start-date", help="Start date for PR analysis (YYYY-MM-DD format, e.g., 2024-01-01)")

    # Read arguments from command line
    args = parser.parse_args()

    # Parse start date if provided
    start_date = None
    if args.start_date:
        try:
            start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
        except ValueError:
            print("Error: start-date must be in YYYY-MM-DD format (e.g., 2024-01-01)")
            exit(1)

    queryOpts = {
        "repo": args.repo,
        "org": args.org
    }

    prs = fetch_pull_requests(args.query, queryOpts, args.token, start_date)

    if isinstance(prs, requests.Response):
        # Error response
        try:
            error_details = prs.json()
        except requests.exceptions.JSONDecodeError:
            error_details = prs.text if prs.text else "No response body"

        print('Error pulling code review data. Status: {}, err: {}'.format(prs.status_code, error_details))
        exit(1)

    print(f"Found {len(prs)} pull requests")
    parsed_prs = parse_into_dicts(prs)
    print_as_csv(parsed_prs, args.file)
    print(f"Data written to {args.file}")


if __name__ == "__main__":
    main()