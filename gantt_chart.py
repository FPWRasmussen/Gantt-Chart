import argparse
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date
import os
from matplotlib.patches import Patch
import matplotlib.dates as mdates

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def gantt_chart(file_path=os.path.join(ROOT_DIR, './gantt.csv'),
                percentage_label="in bar", legend_pos="in plot",
                save_fig = True):
    """
    INPUT:
        file_path : path-like object
            Path to .csv file containing Gantt Chart data
        percentage_label : str
            "in bar" to display task percentage in the bar.
            "after bar" to display the task percentage after the bar.
            Anything else to disable the percentage.
        legend_pos : str
            "in plot" to display the legend in the top right corner.
            "under plot" to display the legend under the plot.
            Anything else to disable the legend.
        save_fig : bool
            Saves the Gantt Chart as a .png file.
    """

    df = pd.read_csv(file_path, delimiter=",", parse_dates=["Start", "End"], dayfirst=True) # Import csv
    df.sort_values(by=['Start'], ignore_index=True, inplace=True, ascending=False)
    df['Completion'].fillna(0, inplace=True)
    df.dropna(inplace=True)
    proj_start = df.Start.min()
    df['start_num'] = (df.Start - proj_start).dt.days
    df['end_num'] = (df.End - proj_start).dt.days
    df['days_start_to_end'] = df.end_num - df.start_num
    df['current_num'] = (df.days_start_to_end * df.Completion)

    c_dict = {'Phase': '#00cd95', 'Task': '#636efb', 'Deadline': '#ef553b'}

    def color(row, c_dict):
        return c_dict[row['Category']]
    
    df['color'] = df.apply(color, axis=1, args=[c_dict])

    fig, ax = plt.subplots(1, figsize=(16, 6))

    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=5, byweekday=0))
    ax.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=0))

    ax.xaxis.grid(which='minor', linestyle=':', linewidth='0.5', color='black', alpha=0.2)
    ax.xaxis.grid(which='major', linestyle='dotted', linewidth='1', color='black', alpha=0.2)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
    plt.xticks(rotation=20, ha='center')

    ax.barh(df.Task, df.current_num, left=df.Start, color=df.color, zorder=2)
    ax.barh(df.Task, df.days_start_to_end, left=df.Start, color=df.color, alpha=0.5, zorder=2)

    for idx, row in df.iterrows():
        if row.Category != "Deadline":
            if percentage_label == "in bar":
                ax.text(row.Start + pd.Timedelta(days=1), idx,
                        f"{int(row.Completion * 100)}%",
                        va='center', alpha=0.8, color="w")
            if percentage_label == "after bar":
                ax.text(row.End + pd.Timedelta(days=0.5), idx,
                        f"{int(row.Completion * 100)}%",
                        va='center', alpha=0.8)

    ax.axvline(date.today(), color="black", ls="dashed", linewidth=1, zorder=3, alpha=0.5)

    legend_elements = [Patch(facecolor=c_dict[i], label=i) for i in c_dict]
    
    if legend_pos == "in plot":
        plt.legend(handles=legend_elements)
    elif legend_pos == "under plot":
        plt.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.075), ncol=99)
    
    plt.suptitle("Master Thesis Gantt Chart")
    plt.tight_layout()
    if save_fig:
        plt.savefig("output/gantt_chart.png")
    plt.show()
    plt.close()
    
def parse_args():
    parser = argparse.ArgumentParser(description="Generate Gantt Chart.")
    parser.add_argument("--file_path", default=os.path.join(ROOT_DIR, './gantt.csv'), help="Path to the CSV file containing Gantt Chart data.")
    parser.add_argument("--percentage_label", default="in bar", choices=["in bar", "after bar", "disable"],
                        help="Label position for task percentage ('in bar', 'after bar', or 'disable').")
    parser.add_argument("--legend_pos", default="in plot", choices=["in plot", "under plot", "disable"],
                        help="Legend position ('in plot', 'under plot', or 'disable').")
    return parser.parse_args()

def main():
    args = parse_args()
    gantt_chart(args.file_path, args.percentage_label, args.legend_pos)

if __name__ == "__main__":
    main()
