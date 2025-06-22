#!/usr/bin/env python3

import pandas as pd
import argparse
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import seaborn as sns

def load_and_prepare_data(csv_file):
    """Load CSV data and prepare it for weekly analysis."""
    df = pd.read_csv(csv_file)
    
    # Convert date columns to datetime
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['merged_at'] = pd.to_datetime(df['merged_at'])
    df['first_reviewed_at'] = pd.to_datetime(df['first_reviewed_at'], errors='coerce')
    
    # Add week column (Monday as start of week)
    df['week_start'] = df['created_at'].dt.to_period('W-MON').dt.start_time
    
    return df

def analyze_by_week_and_author(df):
    """Analyze PR metrics by week and author."""
    # Group by week and author
    weekly_author_stats = df.groupby(['week_start', 'created_by']).agg({
        'number': 'count',  # PR count
        'lines_changed': ['mean', 'sum'],  # Average and total lines changed
        'cycle_time_minutes': 'mean',  # Average cycle time
        'lead_time_minutes': 'mean',  # Average lead time
        'comments_added': 'mean'  # Average comments
    }).round(2)
    
    # Flatten column names
    weekly_author_stats.columns = [
        'pr_count', 'avg_lines_changed', 'total_lines_changed', 
        'avg_cycle_time_minutes', 'avg_lead_time_minutes', 'avg_comments'
    ]
    
    return weekly_author_stats.reset_index()

def create_weekly_analysis_plots(df, weekly_stats, output_dir='.'):
    """Create comprehensive weekly analysis plots."""
    
    # Set up the plotting style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create a large figure with multiple subplots
    fig, axes = plt.subplots(3, 2, figsize=(16, 12))
    fig.suptitle('Weekly PR Metrics Analysis by Author', fontsize=16, fontweight='bold')
    
    # Get unique authors for color coding
    authors = df['created_by'].unique()
    colors = plt.cm.Set3(np.linspace(0, 1, len(authors)))
    author_colors = dict(zip(authors, colors))
    
    # 1. PR Count by Week and Author
    ax1 = axes[0, 0]
    for author in authors:
        author_data = weekly_stats[weekly_stats['created_by'] == author]
        if not author_data.empty:
            ax1.plot(author_data['week_start'], author_data['pr_count'], 
                    marker='o', label=author, color=author_colors[author], linewidth=2)
    
    ax1.set_title('PR Count by Week and Author')
    ax1.set_xlabel('Week Start')
    ax1.set_ylabel('Number of PRs')
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. Average Lines Changed by Week and Author
    ax2 = axes[0, 1]
    for author in authors:
        author_data = weekly_stats[weekly_stats['created_by'] == author]
        if not author_data.empty:
            ax2.plot(author_data['week_start'], author_data['avg_lines_changed'], 
                    marker='s', label=author, color=author_colors[author], linewidth=2)
    
    ax2.set_title('Average Lines Changed by Week and Author')
    ax2.set_xlabel('Week Start')
    ax2.set_ylabel('Average Lines Changed')
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    # 3. Total Lines Changed by Week and Author
    ax3 = axes[1, 0]
    for author in authors:
        author_data = weekly_stats[weekly_stats['created_by'] == author]
        if not author_data.empty:
            ax3.plot(author_data['week_start'], author_data['total_lines_changed'], 
                    marker='^', label=author, color=author_colors[author], linewidth=2)
    
    ax3.set_title('Total Lines Changed by Week and Author')
    ax3.set_xlabel('Week Start')
    ax3.set_ylabel('Total Lines Changed')
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='x', rotation=45)
    
    # 4. Average Cycle Time by Week and Author
    ax4 = axes[1, 1]
    for author in authors:
        author_data = weekly_stats[weekly_stats['created_by'] == author]
        if not author_data.empty:
            ax4.plot(author_data['week_start'], author_data['avg_cycle_time_minutes'], 
                    marker='d', label=author, color=author_colors[author], linewidth=2)
    
    ax4.set_title('Average Cycle Time by Week and Author')
    ax4.set_xlabel('Week Start')
    ax4.set_ylabel('Average Cycle Time (minutes)')
    ax4.grid(True, alpha=0.3)
    ax4.tick_params(axis='x', rotation=45)
    
    # 5. Average Lead Time by Week and Author
    ax5 = axes[2, 0]
    for author in authors:
        author_data = weekly_stats[weekly_stats['created_by'] == author]
        if not author_data.empty:
            ax5.plot(author_data['week_start'], author_data['avg_lead_time_minutes'], 
                    marker='v', label=author, color=author_colors[author], linewidth=2)
    
    ax5.set_title('Average Lead Time by Week and Author')
    ax5.set_xlabel('Week Start')
    ax5.set_ylabel('Average Lead Time (minutes)')
    ax5.grid(True, alpha=0.3)
    ax5.tick_params(axis='x', rotation=45)
    
    # 6. Average Comments by Week and Author
    ax6 = axes[2, 1]
    for author in authors:
        author_data = weekly_stats[weekly_stats['created_by'] == author]
        if not author_data.empty:
            ax6.plot(author_data['week_start'], author_data['avg_comments'], 
                    marker='*', label=author, color=author_colors[author], linewidth=2)
    
    ax6.set_title('Average Comments by Week and Author')
    ax6.set_xlabel('Week Start')
    ax6.set_ylabel('Average Comments')
    ax6.grid(True, alpha=0.3)
    ax6.tick_params(axis='x', rotation=45)
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(f'{output_dir}/weekly_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_author_summary_table(df, weekly_stats, output_dir='.'):
    """Create a summary table of author statistics."""
    
    # Overall author statistics
    author_summary = df.groupby('created_by').agg({
        'number': 'count',  # Total PRs
        'lines_changed': ['mean', 'sum', 'std'],  # Lines changed stats
        'cycle_time_minutes': ['mean', 'median'],  # Cycle time stats
        'lead_time_minutes': ['mean', 'median'],  # Lead time stats
        'comments_added': 'mean'  # Average comments
    }).round(2)
    
    # Flatten column names
    author_summary.columns = [
        'total_prs', 'avg_lines_changed', 'total_lines_changed', 'std_lines_changed',
        'avg_cycle_time', 'median_cycle_time', 'avg_lead_time', 'median_lead_time', 'avg_comments'
    ]
    
    # Add weekly averages
    weekly_avg = weekly_stats.groupby('created_by').agg({
        'pr_count': 'mean',
        'avg_lines_changed': 'mean',
        'avg_cycle_time_minutes': 'mean',
        'avg_lead_time_minutes': 'mean'
    }).round(2)
    
    weekly_avg.columns = ['avg_prs_per_week', 'avg_lines_per_week', 'avg_cycle_time_per_week', 'avg_lead_time_per_week']
    
    # Combine the summaries
    final_summary = pd.concat([author_summary, weekly_avg], axis=1)
    
    # Save to CSV
    final_summary.to_csv(f'{output_dir}/author_summary.csv')
    
    # Print summary
    print("\n=== AUTHOR SUMMARY STATISTICS ===")
    print(final_summary)
    
    return final_summary

def export_weekly_data(weekly_stats, output_dir='.'):
    """Export weekly statistics to CSV."""
    weekly_stats.to_csv(f'{output_dir}/weekly_author_stats.csv', index=False)
    print(f"\nWeekly statistics exported to: {output_dir}/weekly_author_stats.csv")

def main():
    parser = argparse.ArgumentParser(description='Analyze PR metrics by week and author')
    parser.add_argument('csv_file', help='Path to the CSV file with PR metrics')
    parser.add_argument('-o', '--output-dir', default='.', help='Output directory for generated files')
    parser.add_argument('--no-plots', action='store_true', help='Skip generating plots')
    
    args = parser.parse_args()
    
    print(f"Loading data from {args.csv_file}...")
    df = load_and_prepare_data(args.csv_file)
    
    print(f"Analyzing {len(df)} PRs from {df['created_at'].min().date()} to {df['created_at'].max().date()}")
    print(f"Authors found: {', '.join(df['created_by'].unique())}")
    
    # Analyze by week and author
    weekly_stats = analyze_by_week_and_author(df)
    
    # Export weekly data
    export_weekly_data(weekly_stats, args.output_dir)
    
    # Create author summary
    author_summary = create_author_summary_table(df, weekly_stats, args.output_dir)
    
    # Create plots (unless disabled)
    if not args.no_plots:
        print("Generating plots...")
        create_weekly_analysis_plots(df, weekly_stats, args.output_dir)
        print(f"Plots saved to: {args.output_dir}/weekly_analysis.png")
    
    print(f"\nAnalysis complete! Files saved to: {args.output_dir}/")

if __name__ == "__main__":
    main() 