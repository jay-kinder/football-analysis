import xml.etree.ElementTree as et
import pandas as pd
from os import listdir

# ------------------------------------------------------------functions------------------------------------------------------------


def create_df(file, event_type_id="None"):
    x_origin = []
    y_origin = []
    x_destination = []
    y_destination = []
    outcome = []
    minute = []
    half = []
    team = []
    event_type = []
    is_own_goal = []
    is_header = []
    is_freekick = []
    is_assist = []

    team_dict = {
        file[0].attrib["home_team_id"]: file[0].attrib["home_team_name"],
        file[0].attrib["away_team_id"]: file[0].attrib["away_team_name"],
    }

    for game in file:
        for event in game:
            if (
                event.attrib.get("type_id") == str(event_type_id)
                or event_type_id == "None"
            ):
                x_origin.append(event.attrib.get("x"))
                y_origin.append(event.attrib.get("y"))
                outcome.append(event.attrib.get("outcome"))
                minute.append(event.attrib.get("min"))
                half.append(event.attrib.get("period_id"))
                team.append(team_dict[event.attrib.get("team_id")])
                event_type.append(event.attrib.get("type_id"))

                x_destination_value = "0"
                y_destination_value = "0"
                is_own_goal_value = "0"
                is_header_value = "0"
                is_freekick_value = "0"
                is_assist_value = "0"
                for qualifier in event:
                    if qualifier.attrib.get("qualifier_id") == "140":
                        x_destination_value = qualifier.attrib.get("value")
                    if qualifier.attrib.get("qualifier_id") == "141":
                        y_destination_value = qualifier.attrib.get("value")
                    if qualifier.attrib.get("qualifier_id") == "28":
                        is_own_goal_value = "1"
                    if qualifier.attrib.get("qualifier_id") == "15":
                        is_header_value = "1"
                    if qualifier.attrib.get("qualifier_id") == "26":
                        is_freekick_value = "1"
                    if qualifier.attrib.get("qualifier_id") == "210":
                        is_assist_value = "1"
                x_destination.append(x_destination_value)
                y_destination.append(y_destination_value)
                is_own_goal.append(is_own_goal_value)
                is_header.append(is_header_value)
                is_freekick.append(is_freekick_value)
                is_assist.append(is_assist_value)

    column_titles = [
        "team",
        "half",
        "min",
        "x_origin",
        "y_origin",
        "x_destination",
        "y_destination",
        "outcome",
        "event_type",
        "is_own_goal",
        "is_header",
        "is_freekick",
        "is_assist",
    ]
    df = pd.DataFrame(
        data=[
            team,
            half,
            minute,
            x_origin,
            y_origin,
            x_destination,
            y_destination,
            outcome,
            event_type,
            is_own_goal,
            is_header,
            is_freekick,
            is_assist,
        ],
        index=column_titles,
    )
    df = df.T

    # add co-ordinates as float
    df["x_origin"] = df.x_origin.astype(float)
    df["y_origin"] = df.y_origin.astype(float)
    df["x_destination"] = df.x_destination.astype(float)
    df["y_destination"] = df.y_destination.astype(float)

    return df


def create_df_model():
    files = listdir("./model")
    dataframes = []
    for file in files:
        tree = et.ElementTree(file=f"./model/{file}")
        gameFile = tree.getroot()
        dataframes.append(create_df(gameFile))
    df_model = pd.concat(dataframes, ignore_index=True)
    return df_model


# ------------------------------------------------------------variables------------------------------------------------------------
