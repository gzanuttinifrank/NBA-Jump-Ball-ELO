import pandas as pd
import sys
# import os
from elosports.elo import Elo  # https://github.com/ddm7018/Elo


# https://www.reddit.com/r/nba/comments/dhandf/oc_elo_system_to_determine_who_are_the_best_at/
# Looking at the results, the league average rate of scoring first when winning the jump is about 60%.


# def load_obj(name):
#     try:
#         with open(name + '.pkl', 'rb') as f:
#             return pickle.load(f)
#     except:
#         with open(os.path.join(sys._MEIPASS, name+'.pkl'), 'rb') as f:
#             return pickle.load(f)


def padded_input(message):
    txt = input(message+'\n')
    print('')
    if txt == 'exit':
        sys.exit()
    return txt


def name_to_id(name, player_id_dict, ratings_dict):
    lowername = name.lower().strip()
    if lowername == "top":
    	return [lowername]
    matching_ids = list({key for key,value in player_id_dict.items() if value[0].lower()==lowername})
    matches = len(matching_ids)
    if matches == 0:
        return None
    else:
    	if matching_ids[0] not in ratings_dict:
    		return None
    	else:
        	return matching_ids


def handle_input_name(name, player_id_dict, player_team_dict, ratings_dict):
    nameid = name_to_id(name, player_id_dict, ratings_dict)
    while True:
        if not nameid:
            print("Sorry, no player with the name '" + name + "' could be found. Name is either misspelled or he has never taken a jump ball.\n")
            name = padded_input("Try again:")
            nameid = name_to_id(name, player_id_dict, ratings_dict)
            continue
        elif len(nameid) > 1:
            num_names = len(nameid)
            print("There are multiple players with that exact name, here are each of their teams:")
            for i in range(num_names):
                print(str(i+1) + ": " + ', '.join(list(map(lambda x: x[4:], player_team_dict[nameid[i]]))))
            pick = padded_input("\nWhich number player would you like to select?")
            while True:
                try:
                    if int(pick) < num_names+1 and int(pick) > 0:
                        return nameid[int(pick)-1]
                    pick = padded_input("Invalid number entered, try again:")
                except:
                    pick = padded_input("Invalid number entered, try again:")
        elif nameid[0] == "top":
        	topn = padded_input("Enter many players you would like to see:")
        	while True:
	        	try:
	        		topn = int(topn)
	        		break
	        	except:
	        		topn = padded_input("Invalid number, try again:")
        	top_players = [print(player_id_dict[k][0], round(v,2)) for k, v in sorted(ratings_dict.items(), key=lambda item: item[1], reverse=True)[:topn]]
        	print('')
        	nameid = name_to_id(padded_input("Enter a player name:"), player_id_dict, ratings_dict)
        else:
            try:
                player_team_dict[nameid[0]]
                return nameid[0]
            except:
                nameid = name_to_id(padded_input("That player was not active past the specified year. Try again:"), player_id_dict, ratings_dict)


def get_jump_ball_prob(eloLeague, player_id_dict, player_team_dict, ratings_dict):
	p1id = handle_input_name(padded_input("Enter a player name:"), player_id_dict, player_team_dict, ratings_dict)
	p2id = handle_input_name(padded_input("Enter another player name:"), player_id_dict, player_team_dict, ratings_dict)

    # Get expected win prob
	p1_win_prob = eloLeague.expectResult(ratings_dict[p1id],ratings_dict[p2id])
	print(player_id_dict[p1id][0] + "'s jump ball win probability is: " + str(round(p1_win_prob,4)) + "\n")


if __name__ == '__main__':

	# player_id_dict = load_obj('Data/player_id_dict')
	# player_team_dict = load_obj('Data/player_team_dict')
	# ratings_dict = load_obj('Data/jump_ball_ratings_dict.pkl')
	player_id_dict = pd.read_pickle('Data/player_id_dict.pkl')
	player_team_dict = pd.read_pickle('Data/player_team_dict.pkl')
	ratings_dict = pd.read_pickle('Data/jump_ball_ratings_dict.pkl')

	eloLeague = Elo(k = 40)

	print("\nWelcome! Enter two NBA player names to see the result of their jump ball matchup. Type 'exit' at any time to terminate the application.\n")
	while True:
	    get_jump_ball_prob(eloLeague, player_id_dict, player_team_dict, ratings_dict)



