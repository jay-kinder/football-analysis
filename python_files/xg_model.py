from functions import create_df_model
import pandas as pd
import numpy as np
from matplotlib import rcParams
from mplsoccer.pitch import VerticalPitch
import statsmodels.formula.api as smf
import statsmodels.api as sm
import matplotlib.pyplot as plt
from collections import OrderedDict

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

#create dataframe
df = create_df_model()

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------
def xG_model(df):
    #create empty df to hold calculations & list of shot event numbers
    shots_model=pd.DataFrame(columns=["goal","x","y"])
    shot_ids = ["13", "14", "15", "16"]

    for i,row in df.iterrows():
        if row["event_type"] in shot_ids and row["is_own_goal"] != "1":
            x = shots_model.at[i,'x']=row["x_origin"]
            y = shots_model.at[i,'y']=row["y_origin"]
            c = shots_model.at[i,'c']=abs(row["y_origin"]-50)

            shots_model.at[i,'distance']= round(100 - np.sqrt(x**2 + c**2), 1)

            a1 = np.arctan((c-3.66)/(100-x))
            a2 = np.arctan((100-x)/(c+3.66))
            a = (np.pi/2)-(a1 + a2)
            shots_model.at[i,'angle'] = round(a * (180/np.pi), 1)

            shots_model.at[i,'goal']=0
            if row["event_type"] == "16":
                shots_model.at[i,'goal']=1
    
    #two dimensional histogram
    H_Shot=np.histogram2d(shots_model['y'], shots_model['x'],bins=50,range=[[0, 100],[0, 100]])
    goals_only=shots_model[shots_model['goal']==1]
    H_Goal=np.histogram2d(goals_only['y'], goals_only['x'],bins=50,range=[[0, 100],[0, 100]])

    #plot the probability of scoring from different points
    pitch = VerticalPitch(figsize=(16, 11), line_zorder=2, pitch_type='opta', orientation='vertical', half=True, pitch_color='white', line_color='black')
    fig,ax = pitch.draw()
    np.seterr(divide='ignore', invalid='ignore')
    pos = ax.imshow(H_Goal[0].T/H_Shot[0].T, extent=[0,100,0,100], origin='lower', aspect='auto', cmap=plt.cm.BuGn, zorder=1)
    fig.colorbar(pos, ax=ax)
    ax.annotate("Proportion of shots resulting in a goal", (100, 102), ha='left', fontsize=10)
    fig.savefig('static/ProbabilityOfScoring.png', bbox_inches="tight", dpi=200) 

    #Show how goal angle predicts probability of scoring
    # shotcount_dist=np.histogram(shots_model['angle'],bins=40,range=[0, 150])
    # goalcount_dist=np.histogram(goals_only['angle'],bins=40,range=[0, 150])
    # prob_goal=np.divide(goalcount_dist[0],shotcount_dist[0])
    # angle=shotcount_dist[1]
    # midangle= (angle[:-1] + angle[1:])/2
    # fig,ax=plt.subplots(num=2)
    # ax.plot(midangle, prob_goal, linestyle='none', marker= '.', markerSize= 12, color='black')
    # ax.set_ylabel('Probability chance scored')
    # ax.set_xlabel("Shot angle")
    # ax.spines['top'].set_visible(False)
    # ax.spines['right'].set_visible(False)
    # b=[3, -3]
    # x=np.arange(150,step=0.1)
    # y=1/(1+np.exp(b[0]+b[1]*x*np.pi/180)) 
    # ax.plot(x, y, linestyle='solid', color='black')
    # plt.savefig('static/angle_to_goal_prob.png', bbox_inches="tight")
    # plt.clf()

    #angle to goal/misses
    # xG=1/(1+np.exp(b[0]+b[1]*shots_model['angle']*np.pi/180))
    # shots_model = round(shots_model.assign(xG=xG), 2)
    # fig,ax=plt.subplots(num=1)
    # ax.plot(shots_model['angle'], shots_model['goal'], linestyle='none', marker= '.', markerSize= 12, color='black')
    # ax.plot(x, y, linestyle='solid', color='black')
    # ax.plot(x, 1-y, linestyle='solid', color='black')
    # loglikelihood=0
    # for item,shot in shots_model.iterrows():
    #     ang=shot['angle']
    #     if shot['goal']==1:
    #         loglikelihood=loglikelihood+np.log(shot['xG'])
    #         ax.plot([ang,ang],[shot['goal'],shot['xG']], color='red')
    #     else:
    #         loglikelihood=loglikelihood+np.log(1 - shot['xG'])
    #         ax.plot([ang,ang],[shot['goal'],1-shot['xG']], color='blue')
        
    # ax.set_ylabel('Goal scored')
    # ax.set_xlabel("Shot angle")
    # plt.ylim((-0.05,1.05))
    # plt.xlim((0,140))
    # plt.text(110,0.2,'Log-likelihood:') 
    # plt.text(110,0.1,str(loglikelihood))
    # ax.set_yticks([0,1])
    # ax.spines['top'].set_visible(False)
    # ax.spines['right'].set_visible(False)
    # plt.savefig('static/model_fit.png', bbox_inches="tight")
    # plt.clf()

    #a general model for fitting goal probability
    model_variables = ['angle','distance']
    model=''
    for v in model_variables[:-1]:
        model = model  + v + ' + '
    model = model + model_variables[-1]
    test_model = smf.glm(formula="goal ~ " + model, data=shots_model, family=sm.families.Binomial()).fit()
    # print(test_model.summary())        
    b=test_model.params

    def calculate_xG(sh):    
        bsum=b[0]
        for i,v in enumerate(model_variables):
            bsum=bsum+b[i+1]*sh[v]
        xG = 1/(1+np.exp(bsum)) 
        return xG 
    
    xG=shots_model.apply(calculate_xG, axis=1) 
    shots_model = round(shots_model.assign(xG=xG), 2)


def all_shots_by_type(df):
    #set default text colour
    rcParams['text.color'] = 'white'

    #draw the pitch
    pitch = VerticalPitch(figsize=(16, 11), pad_top=7, pitch_type='opta', orientation='vertical', half=True, pitch_color='#696969', line_color='white')
    fig, ax = pitch.draw()

    for i, row in df.iterrows():
        marker_position = row["x_origin"], row["y_origin"]
        if row["event_type"] == "16":      
            if row["is_own_goal"] == "1":
                continue
            if row["is_header"] == "1":
                pitch.scatter(marker_position[0], marker_position[1], marker="o", color="#000080", edgecolors="white", s=100, label="Header", ax=ax)
            elif row["is_freekick"] == "1":
                pitch.scatter(marker_position[0], marker_position[1], marker="^", color="#FDD023", edgecolors="white", s=100, label="Freekick", ax=ax)
            else:
                pitch.scatter(marker_position[0], marker_position[1], marker="H", color="#6d2aff", edgecolors="white", s=100, label="Foot", ax=ax)

        if row["event_type"] == "13" or row["event_type"] == "14" or row["event_type"] == "15":        
            if row["is_header"] == "1":
                pitch.scatter(marker_position[0], marker_position[1], marker="o", color="none", edgecolors="white", s=60, label="Miss", ax=ax)
            elif row["is_freekick"] == "1":
                pitch.scatter(marker_position[0], marker_position[1], marker="^", color="none", edgecolors="white", s=60, ax=ax)
            else:
                pitch.scatter(marker_position[0], marker_position[1], marker="H", color="none", edgecolors="white", s=60, ax=ax)

    #add legend and title
    handles, labels = plt.gca().get_legend_handles_labels()
    legend_labels = OrderedDict(zip(labels, handles))
    ax.legend(legend_labels.values(), legend_labels.keys(), facecolor='#696969', edgecolor='None', loc='lower right', fontsize=7, handlelength=4, ncol=2, labelspacing=1)
    ax.annotate("All Shots/Goals From All Reported Games (in Model)", (100, 102), ha='left', fontsize=10)

    #save file
    fig.savefig(f"static/all_shots_from_model.png", bbox_inches="tight", pad_inches=0, dpi=200)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

xG_model(df)
all_shots_by_type(df)
