#! /bin/bash

echo "Creating Visualisations..."
echo "----------------------------------"
for file in $1/*; 
do
python3 python_files/game_passing_visualisations.py $file
python3 python_files/game_shooting_visualisations.py $file
done
python3 python_files/team_player_heatmaps.py
python3 python_files/xg_model.py
echo "Visualisations saved in the static folder"
