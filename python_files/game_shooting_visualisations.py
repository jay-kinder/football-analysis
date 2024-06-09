import xml.etree.ElementTree as et
import sys
from functions import create_df
from matplotlib import rcParams
from mplsoccer.pitch import VerticalPitch
import matplotlib.pyplot as plt
from collections import OrderedDict

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------

# import file
tree = et.ElementTree(file=sys.argv[1])
gameFile = tree.getroot()

# create dataframe
shooting_data = create_df(gameFile)

# get variables needed for labelling
home_team = gameFile[0].attrib["home_team_name"]
away_team = gameFile[0].attrib["away_team_name"]
game_date = gameFile[0].attrib["game_date"].split("T")[0]
game_score = f"{gameFile[0].attrib['home_score']}-{gameFile[0].attrib['away_score']}"
competition_name = gameFile[0].attrib["competition_name"]

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------


# add team successful/unsuccessful shots to chart
def team_shooting(df, team):
    # set default text colour
    rcParams["text.color"] = "#c7d5cc"

    # draw the pitch
    pitch = VerticalPitch(
        figsize=(12, 8),
        pad_top=25,
        pad_bottom=10,
        pitch_type="opta",
        orientation="vertical",
        half=True,
        pitch_color="#1c4966",
        line_color="#c7d5cc",
    )
    fig, ax = pitch.draw()

    for i, row in df.iterrows():
        if row["team"] == team:
            marker_position = row["x_origin"], row["y_origin"]
            if row["event_type"] == "13" or row["event_type"] == "14":
                pitch.scatter(
                    marker_position[0],
                    marker_position[1],
                    marker="o",
                    color="#cb2c31",
                    s=80,
                    label="Off Target",
                    ax=ax,
                )
            if row["event_type"] == "15":
                pitch.scatter(
                    marker_position[0],
                    marker_position[1],
                    marker="o",
                    color="#8cff9e",
                    s=80,
                    label="On Target",
                    ax=ax,
                )
            if row["event_type"] == "16":
                if row["is_own_goal"] == "1":
                    pitch.scatter(
                        100 - marker_position[0],
                        100 - marker_position[1],
                        marker="football",
                        c="red",
                        edgecolors="black",
                        s=120,
                        label="Own Goal",
                        ax=ax,
                    )
                else:
                    pitch.scatter(
                        marker_position[0],
                        marker_position[1],
                        marker="football",
                        s=120,
                        label="Goal",
                        ax=ax,
                    )

    # add legend and title
    handles, labels = plt.gca().get_legend_handles_labels()
    legend_labels = OrderedDict(zip(labels, handles))
    ax.legend(
        legend_labels.values(),
        legend_labels.keys(),
        facecolor="#1c4966",
        edgecolor="None",
        loc="lower left",
        fontsize=7,
        handlelength=3,
        ncol=2,
        labelspacing=1,
    )
    ax.annotate(
        f"{home_team}({game_score[0]}) vs {away_team}({game_score[2]})\n{competition_name}, {game_date}\n \n {team} Shooting",
        (100, 105),
        ha="left",
        fontsize=10,
    )

    # save file
    fig.savefig(
        f"static/{home_team.replace(' ','-').lower()}_{away_team.replace(' ','-').lower()}_{game_date}_{team}_fullshooting.png",
        bbox_inches="tight",
        pad_inches=0,
        dpi=200,
    )


# add team goal buildup to chart
def team_goal_buildup(df, team):
    # set default text colour
    rcParams["text.color"] = "#c7d5cc"

    # draw the pitch
    pitch = VerticalPitch(
        figsize=(12, 8),
        pad_top=25,
        pad_bottom=10,
        pitch_type="opta",
        orientation="vertical",
        half=True,
        pitch_color="#222222",
        line_color="#c7d5cc",
    )
    fig, ax = pitch.draw()

    assist = []
    for i, row in df.iterrows():
        if row["team"] == team:
            if row["is_assist"] == "1":
                assist = (
                    row["x_origin"],
                    row["y_origin"],
                    row["x_destination"],
                    row["y_destination"],
                )
            if row["event_type"] in ["13", "14", "15"]:
                assist = []
            if row["event_type"] == "16":
                marker_position = row["x_origin"], row["y_origin"]
                if row["is_own_goal"] == "1":
                    pitch.scatter(
                        100 - marker_position[0],
                        100 - marker_position[1],
                        marker="football",
                        c="red",
                        edgecolors="black",
                        s=120,
                        label="Own Goal",
                        ax=ax,
                    )
                else:
                    if assist:
                        pitch.lines(
                            assist[2],
                            assist[3],
                            marker_position[0],
                            marker_position[1],
                            lw=1,
                            color="#8cff9e",
                            linestyles="dashed",
                            label="Dribble",
                            ax=ax,
                        )
                        pitch.lines(
                            assist[0],
                            assist[1],
                            assist[2],
                            assist[3],
                            lw=2,
                            transparent=True,
                            comet=True,
                            color="pink",
                            label="Assist",
                            ax=ax,
                        )
                    pitch.scatter(
                        marker_position[0],
                        marker_position[1],
                        marker="football",
                        s=120,
                        label="Goal",
                        zorder=3,
                        ax=ax,
                    )
                assist = []

    # add legend and title
    handles, labels = plt.gca().get_legend_handles_labels()
    legend_labels = OrderedDict(zip(labels, handles))
    ax.legend(
        legend_labels.values(),
        legend_labels.keys(),
        facecolor="#222222",
        edgecolor="None",
        loc="lower left",
        fontsize=7,
        handlelength=3,
        ncol=2,
        labelspacing=1,
    )
    ax.annotate(
        f"{home_team}({game_score[0]}) vs {away_team}({game_score[2]})\n{competition_name}, {game_date}\n \n {team} Goal Buildup",
        (100, 105),
        ha="left",
        fontsize=10,
    )

    # save file
    fig.savefig(
        f"static/{home_team.replace(' ','-').lower()}_{away_team.replace(' ','-').lower()}_{game_date}_{team}_goalbuildup.png",
        bbox_inches="tight",
        pad_inches=0,
        dpi=200,
    )


# -----------------------------------------------------------------------------------------------------------------------------------------------------------------

team_shooting(shooting_data, home_team)
team_goal_buildup(shooting_data, home_team)
team_shooting(shooting_data, away_team)
team_goal_buildup(shooting_data, away_team)
