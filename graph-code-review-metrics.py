#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import argparse

## 
## Visualization of wait time to total lines of code changed
##
def graph_loc_to_wait(df):
    fig, ax = plt.subplots()
    ax.scatter(df.lines_changed, df.cycle_time_minutes, alpha=0.5)

    ax.set_xlabel('Lines Changed', fontsize=15)
    ax.set_ylabel('Total Cycle Time (Wait Time)', fontsize=15)
    ax.set_xticks([])
    ax.set_yticks([])

    ax.grid(True)
    fig.tight_layout()

    plt.show()

def graph_lead_per_loc(df):
    df['lead_per_loc'] = df.lead_time_minutes / df.lines_changed

    fig, ax = plt.subplots()
    ax.scatter(df.lines_changed, df.lead_per_loc, alpha=0.5)

    ax.set_xlabel('Lines Changed', fontsize=15)
    ax.set_ylabel('Lead Time per Size (Lead Time /  LoC)', fontsize=15)
    ax.set_xticks([])
    ax.set_yticks([])

    ax.grid(True)
    fig.tight_layout()

    plt.show()

##
## Visualization of wait time per lines of code to total lines of code changed
## Wait time (minute/loc) is a proxy for throughput per size of the pr
##
def graph_minutes_per_loc(df):
    df['wait_per_loc'] = df.cycle_time_minutes / df.lines_changed

    fig, ax = plt.subplots()
    ax.scatter(df.lines_changed, df.wait_per_loc, alpha=0.5)

    ax.set_xlabel('Lines Changed', fontsize=15)
    ax.set_ylabel('Wait Time per Size (Wait Time /  LoC)', fontsize=15)
    ax.set_xticks([])
    ax.set_yticks([])

    ax.grid(True)
    fig.tight_layout()

    plt.show()

##
## Visualization of comments added to total lines of code changed
## Proxy for "engagement" of a pr
##
def graph_engagement_per_loc(df):
    fig, ax = plt.subplots()
    ax.scatter(df.lines_changed, df.comments_added, alpha=0.5)

    ax.set_xlabel('Lines Changed', fontsize=15)
    ax.set_ylabel('Comments Added (Engagement)', fontsize=15)
    ax.set_xticks([])
    ax.set_yticks([])

    ax.grid(True)
    fig.tight_layout()

    plt.show()

def main():
    # Initialize parser
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-f", "--file", help = "The path to the csv file to read")

    args = parser.parse_args()

    df = pd.read_csv(args.file)

    graph_loc_to_wait(df)
    graph_minutes_per_loc(df)
    graph_lead_per_loc(df)
    graph_engagement_per_loc(df)

if __name__ == "__main__":
    main()