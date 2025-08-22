import streamlit as st
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
from mplsoccer import Pitch

st.set_page_config(layout="wide")

left_col, center_col, right_col = st.columns([1, 2, 1], gap="large")

df = pd.read_excel("fcsb.xlsx")
df["BirthDate"] = pd.to_datetime(df["BirthDate"], dayfirst=True, errors="coerce")
df["StartDate"] = pd.to_datetime(df["StartDate"], dayfirst=True, errors="coerce")
df["EndDate"] = pd.to_datetime(df["EndDate"], dayfirst=True, errors="coerce")
today = pd.to_datetime(dt.date.today())
df["Age"] = (today - df["BirthDate"]).dt.days / 365.25
df["AgeStart"] = (df["StartDate"] - df["BirthDate"]).dt.days / 365.25
df["AgeEnd"] = (df["EndDate"] - df["BirthDate"]).dt.days / 365.25
df["YearsAtClub"] = (today - df["StartDate"]).dt.days / 365.25

def map_color(series):
    min_val, max_val = series.min(), series.max()
    def inner(val):
        norm = (val - min_val) / (max_val - min_val + 1e-6)
        return mcolors.to_hex(plt.cm.RdYlGn(norm))
    return inner

with left_col:
    zone_goals = df.groupby("Position")["Goals"].sum()
    color_func = map_color(zone_goals)

    pitch = Pitch(pitch_type='custom', pitch_length=100, pitch_width=100, line_color='black')
    fig_goals, ax_goals = plt.subplots(figsize=(6, 10))
    pitch.draw(ax=ax_goals)
    ax_goals.set_title("Goals per Position", fontsize=14)

    zones = {
        "LB": (0, 15, 30, 18),
        "CB": (35, 10, 30, 18),
        "RB": (70, 15, 30, 18),
        "CDM": (35, 35, 30, 20),
        "LM": (0, 55, 30, 18),
        "RM": (70, 55, 30, 18),
        "CAM": (35, 60, 30, 18),
        "ST": (35, 82, 30, 18), 
    }

    for pos, (x0, y0, w, h) in zones.items():
        total = zone_goals.get(pos, 0)
        rect = plt.Rectangle((y0, x0), h, w, color=color_func(total), alpha=0.5)
        ax_goals.add_patch(rect)

        # Sort players by Goals decreasingly
        players = df[df["Position"] == pos].sort_values(by="Goals", ascending=False)
        text = "\n".join([f"{row['Name']} ({row['Goals']})" for _, row in players.iterrows()])
        ax_goals.text(y0 + h/2, x0 + w/2, f"{pos}\n{total}\n{text}", ha="center", va="center", fontsize=9)

    ax_goals.invert_yaxis()
    ax_goals.set_aspect('equal')
    st.pyplot(fig_goals)

    st.subheader("Top Marcatori")
    top5 = df.sort_values(by="Goals", ascending=False).head(6)
    nr = 1
    for i, row in top5.iterrows():
        st.write(f"{nr}. {row['Name']} ({row['Goals']} goluri)")
        nr+=1

with center_col:
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axvspan(24, 30, color="gray", alpha=0.3)
    for m in [200, 400, 600, 800, 1000]:
        ax.axhline(y=m, color="lightgray", linestyle="--", linewidth=0.8)

    xmin, xmax = int(df["Age"].min()) - 2, int(df["Age"].max()) + 2
    for age in range(xmin, xmax + 1, 2):
        ax.axvline(x=age, color="lightgray", linestyle="--", linewidth=0.8)

    for _, row in df.iterrows():
        ax.hlines(y=row["Minutes played"], xmin=row["AgeStart"], xmax=row["AgeEnd"], color="black", alpha=0.6)
        if row["YearsAtClub"] > 1:
            ax.scatter(row["Age"], row["Minutes played"], color="purple", s=70, zorder=3)
        else:
            ax.scatter(row["Age"], row["Minutes played"], color="red", marker="x", s=80, zorder=3)
        ax.text(row["Age"], row["Minutes played"] + 30, row["Name"], fontsize=8)

    ax.set_xlabel("Age")
    ax.set_ylabel("Minutes Played")
    ax.set_title("Squad Age Profile")
    ax.set_xlim(xmin, xmax)

    purple_dot = mpatches.Patch(color='purple', label='Years > 1')
    red_x = mpatches.Patch(color='red', label='Years ≤ 1')
    gray_patch = mpatches.Patch(color='gray', alpha=0.3, label='Peak Years (24–30)')
    ax.legend(handles=[purple_dot, red_x, gray_patch], loc="upper left")
    st.pyplot(fig)

    bins = [15, 19, 25, 31, 40]
    labels = ["<19", "20-24", "25-30", "30+"]
    df["AgeGroup"] = pd.cut(df["Age"], bins=bins, labels=labels, right=False)
    age_counts = df["AgeGroup"].value_counts().sort_index()
    feb2024_counts = pd.Series([1, 5, 9, 9], index=labels)

    fig2, ax2 = plt.subplots(figsize=(10, 2.8))
    width = 0.35
    age_counts.plot(kind="bar", ax=ax2, width=width, color="steelblue", edgecolor="black", position=0, label="Current")
    feb2024_counts.plot(kind="bar", ax=ax2, width=width, color="orange", edgecolor="black", position=1, label="Ian 2024")
    ax2.set_xlim(-0.5, len(labels)-0.5)
    ax2.set_xlabel("Age Group")
    ax2.set_ylabel("Number of Players")
    ax2.set_title("Players per Age Group (Current vs 15 Ian 2024)")
    ax2.legend()
    st.pyplot(fig2)

with right_col:
    if "Salariu" in df.columns:
        zone_salary = df.groupby("Position")["Salariu"].mean()
        color_func_salary = map_color(zone_salary)

        pitch = Pitch(pitch_type='custom', pitch_length=100, pitch_width=100, line_color='black')
        fig_salary, ax_salary = plt.subplots(figsize=(6, 9))
        pitch.draw(ax=ax_salary)
        ax_salary.set_title("Average Salary per Position", fontsize=14)

        zones = {
            "GK": (30, 0, 40, 16),
            "LB": (0, 18, 30, 18),
            "CB": (35, 18, 30, 18),
            "RB": (70, 18, 30, 18),
            "CDM": (35, 40, 30, 20),
            "LM": (0, 55, 30, 18),
            "RM": (70, 55, 30, 18),
            "CAM": (35, 62, 30, 18),
            "ST": (35, 82, 30, 18), 
        }

        for pos, (x0, y0, w, h) in zones.items():
            avg_salary = zone_salary.get(pos, 0)
            rect = plt.Rectangle((y0, x0), h, w, color=color_func_salary(avg_salary), alpha=0.5)
            ax_salary.add_patch(rect)

            players = df[df["Position"] == pos].sort_values(by="Salariu", ascending=False)
            text = "\n".join([f"{row['Name']} ({row['Salariu']})" for _, row in players.iterrows()])
            ax_salary.text(y0 + h/2, x0 + w/2, f"{pos}\n{avg_salary:.1f}\n{text}", ha="center", va="center", fontsize=8)

        ax_salary.invert_yaxis()
        ax_salary.set_aspect('equal')
        st.pyplot(fig_salary)

        total_salary = df["Salariu"].sum()
        st.markdown(f"**Total Salary: {total_salary:.1f}* k")

        if "Valoare" in df.columns:
            zone_value = df.groupby("Position")["Valoare"].sum()
            color_func_value = map_color(zone_value)

            fig_value, ax_value = plt.subplots(figsize=(6, 9))
            pitch.draw(ax=ax_value)
            ax_value.set_title("Player Values per Position", fontsize=14)

            for pos, (x0, y0, w, h) in zones.items():
                avg_val = zone_value.get(pos, 0)
                rect = plt.Rectangle((y0, x0), h, w, color=color_func_value(avg_val), alpha=0.5)
                ax_value.add_patch(rect)

                players = df[df["Position"] == pos].sort_values(by="Valoare", ascending=False).head(10)
                text = "\n".join([f"{row['Name']} ({row['Valoare']})" for _, row in players.iterrows()])
                ax_value.text(y0 + h/2, x0 + w/2, f"{pos}\n{avg_val:.1f}\n{text}", ha="center", va="center", fontsize=8 )

            ax_value.invert_yaxis()
            ax_value.set_aspect('equal')
            st.pyplot(fig_value)
        else:
            st.warning("Value column not found in the dataset.")

    else:
        st.warning("Salary column not found in the dataset.")