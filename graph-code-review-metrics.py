#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import argparse

## 
## Visualization of cycle time to total lines of code changed
## This is meant to see if the number of lines does actually affect 
## the cycle time of the pull request
##
def graph_cycle_time(ax, df):
    p = ax[0, 0]
    p.scatter(df.lines_changed, df.cycle_time_minutes, alpha=0.5)

    p.set_xlabel('Lines Changed', fontsize=15)
    p.set_ylabel('Cycle Time', fontsize=15)
    p.set_xticks([])
    p.set_yticks([])
    p.grid(True)
    p.set_title('Cycle Time')

## 
## Visualization of cycle time per line to total lines of code changed
## This is meant to see if the total lines of code changed affects that overall
## cycle time of each line of code. 
## i.e. - if having 10 lines of code has a faster "cycle time per line" than 100 lines of code
##
def graph_cycle_time_per_line(ax, df):
    df['cycle_per_loc'] = df.cycle_time_minutes / df.lines_changed

    p = ax[0, 1]
    p.scatter(df.lines_changed, df.cycle_per_loc, alpha=0.5)

    p.set_xlabel('Lines Changed', fontsize=15)
    p.set_ylabel('Cycle Time per Line (Cycle /  LoC)', fontsize=15)
    p.set_xticks([])
    p.set_yticks([])
    p.grid(True)
    p.set_title('Cycle Time per Line')

## 
## Visualization of cycle time per line to total lines of code changed
## This is meant to see if the total lines of code changed affects that overall
## lead time of each line of code. 
## i.e. - if having 10 lines of code has a faster "lead time per line" than 100 lines of code
##
def graph_lead_time_per_loc(ax, df):
    df['lead_per_loc'] = df.lead_time_minutes / df.lines_changed

    p = ax[1, 0]
    p.scatter(df.lines_changed, df.lead_per_loc, alpha=0.5)

    p.set_xlabel('Lines Changed', fontsize=15)
    p.set_ylabel('Lead Time per Line (Lead /  LoC)', fontsize=15)
    p.set_xticks([])
    p.set_yticks([])
    p.grid(True)
    p.set_title('Lead Time per Line')


##
## Visualization of comments added to total lines of code changed
## Proxy for "engagement" of a pr.
##
def graph_engagement(ax, df):
    p = ax[1, 1]
    p.scatter(df.lines_changed, df.comments_added, alpha=0.5)

    p.set_xlabel('Lines Changed', fontsize=15)
    p.set_ylabel('Comments Added (Engagement)', fontsize=15)
    p.set_xticks([])
    p.set_yticks([])
    p.grid(True)
    p.set_title('Engagement')
 
def main():
    # Initialize parser
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-f", "--file", help = "The path to the csv file to read")

    args = parser.parse_args()

    df = pd.read_csv(args.file)

    fig, ax = plt.subplots(2, 2)

    graph_cycle_time(ax, df)
    graph_cycle_time_per_line(ax, df)
    graph_lead_time_per_loc(ax, df)
    graph_engagement(ax, df)

    fig.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()