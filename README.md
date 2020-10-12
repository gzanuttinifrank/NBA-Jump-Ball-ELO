# NBA-Jump-Ball-ELO
#### ELO ratings for NBA players to quantify their skill at winning jump balls

This project was designed due to the dearth of publicly available statistics regarding jump balls in the NBA. It scrapes `basketball-reference.com`'s play-by-play logs and creates ELO ratings for all players who took at least one jump ball in the specified time frame (the data provided begins at the start of the 2014-2015 season). Once the data is gathered and the ratings created, it is then possible to predict relative strengths of players and thus probabilities for head-to-head matchups, regardless of whether they have faced one another in the past. This could in theory be useful for betting on which team will score the first basket of a game, but its potential profitability has not yet been tested.

`bball_ref_pbp.py` has functions to create and update both the dataframe recording all jump ball results as well as the ELO ratings.

`elo_ratings.py` prompts the user to input two NBA player names, checks for their existence in the dataset, and if both are found, returns the first player's jump ball win probability against the second.
