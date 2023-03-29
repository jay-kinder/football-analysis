from matplotlib import rcParams
from mplsoccer.pitch import VerticalPitch
from functions import create_df_model

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

def team_all_goals_distribution(df, team):
    rcParams['text.color'] = '#c7d5cc'
    pitch = VerticalPitch(figsize=(12, 8), pad_top=10, line_zorder=2, pitch_type='opta', orientation='vertical', half=True, pitch_color='#301934', line_color='#c7d5cc')
    fig, ax = pitch.draw()    
    marker_position_x = []
    marker_position_y = []
    for i, row in df.iterrows():
        if row["team"] == team:
            if row["event_type"] == "16":
                if row["is_own_goal"] == "1":
                    continue
                else:
                    marker_position_x.append(row["x_origin"])
                    marker_position_y.append(row["y_origin"])

    pitch.kdeplot(marker_position_x, marker_position_y, cmap='cool', linewidths=3, label="More Goals", ax=ax)
    ax.collections[0].set_alpha(0)
    
    ax.legend(facecolor='#301934', edgecolor='None', loc='lower left', bbox_to_anchor=(0.05, 0.05), fontsize=7, handlelength=3)
    ax.annotate(f"{team} Goal Distribution", (100, 102), ha='left', fontsize=10)
    fig.savefig(f"static/{team.replace(' ','-').lower()}_goal_distribution.png", bbox_inches="tight", pad_inches=0, dpi=200)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

team_all_goals_distribution(create_df_model(), "Middlesbrough U18")