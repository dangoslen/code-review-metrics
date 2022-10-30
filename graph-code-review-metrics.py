#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt

## 
## Visualization of wait time to total lines of code changed
##
def graph_loc_to_wait():
    df = pd.read_csv('code_review_metrics.csv')

    fig, ax = plt.subplots()
    ax.scatter(df.lines_changed, df.cycle_time_minutes, alpha=0.5)

    ax.set_xlabel('Lines Changed', fontsize=15)
    ax.set_ylabel('Total Cycle Time (Wait Time)', fontsize=15)
    ax.set_xticks([])
    ax.set_yticks([])

    ax.grid(True)
    fig.tight_layout()

    plt.show()

##
## Visualization of wait time per lines of code to total lines of code changed
## Wait time (minute/loc) is a proxy for throughput per size of the pr
##
def graph_minutes_per_loc():
    df = pd.read_csv('code_review_metrics.csv')

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
def graph_engagement_per_loc():
    df = pd.read_csv('code_review_metrics.csv')

    fig, ax = plt.subplots()
    ax.scatter(df.lines_changed, df.comments_added, alpha=0.5)

    ax.set_xlabel('Lines Changed', fontsize=15)
    ax.set_ylabel('Comments Added (Engagement)', fontsize=15)
    ax.set_xticks([])
    ax.set_yticks([])

    ax.grid(True)
    fig.tight_layout()

    plt.show()

if __name__ == "__main__":
    graph_loc_to_wait()
    graph_minutes_per_loc()
    graph_engagement_per_loc()