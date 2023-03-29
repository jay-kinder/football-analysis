import xml.etree.ElementTree as et
import sys
from functions import create_df
from matplotlib import rcParams
from mplsoccer.pitch import Pitch
import matplotlib.pyplot as plt
from collections import OrderedDict

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

#import file
tree = et.ElementTree(file = sys.argv[1])
gameFile = tree.getroot()

#create dataframe
pass_data = create_df(gameFile, 1)

#get variables needed for labelling
home_team = gameFile[0].attrib["home_team_name"]
away_team = gameFile[0].attrib["away_team_name"]
game_date = gameFile[0].attrib["game_date"].split("T")[0]
game_score = f"{gameFile[0].attrib['home_score']}-{gameFile[0].attrib['away_score']}"
competition_name = gameFile[0].attrib["competition_name"]

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

#add team successful/unsuccessful passes to chart
def team_passing(df, team, type="all"):
    #set default text colour
    rcParams['text.color'] = '#c7d5cc'

    #draw the pitch
    pitch = Pitch(figsize=(16, 11), pad_top=25, pad_bottom=10, pitch_type='opta', orientation='horizontal', view='full', pitch_color='#222222', line_color='#c7d5cc')
    fig, ax = pitch.draw() 

    for i, row in df.iterrows():
        if row["team"] == team:
            line_origin = row["x_origin"], row["y_origin"]
            line_dest = row["x_destination"], row["y_destination"]
            if row["outcome"] == "1":
                line_colour = "#44bcd8"
                label = "Successful Passes"
            else:
                line_colour = "#e07b39"
                label = "Unsuccessful Passes"            
            if type == "all":
                pitch.arrows(line_origin[0], line_origin[1], line_dest[0], line_dest[1], width=1, headwidth=5, headlength=5, color=line_colour, label=label, ax=ax)
            if type == "successful" and row["outcome"] == "1":
                pitch.lines(line_origin[0], line_origin[1], line_dest[0], line_dest[1], lw=2, transparent=True, comet=True, color=line_colour, label=label, ax=ax)
            if type == "unsuccessful" and row["outcome"] == "0":
                pitch.lines(line_origin[0], line_origin[1], line_dest[0], line_dest[1], lw=2, transparent=True, comet=True, color=line_colour, label=label, ax=ax)

    #add legend and title
    handles, labels = plt.gca().get_legend_handles_labels()
    legend_labels = OrderedDict(zip(labels, handles))
    ax.legend(legend_labels.values(), legend_labels.keys(), facecolor='#222222', edgecolor='None', loc='lower left', fontsize=7, handlelength=4, ncol=2)
    ax.annotate(f"{home_team}({game_score[0]}) vs {away_team}({game_score[2]})\n{competition_name}, {game_date}\n \n {team} {type.capitalize()} Passing", (0, 105), ha='left', fontsize=10)

    #save file
    fig.savefig(f"static/{home_team.replace(' ','-').lower()}_{away_team.replace(' ','-').lower()}_{game_date}_{team}_{type}passing.png", bbox_inches="tight", pad_inches=0, dpi=200)
    
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

team_passing(pass_data, home_team, "successful")
team_passing(pass_data, home_team, "unsuccessful")
team_passing(pass_data, away_team)
