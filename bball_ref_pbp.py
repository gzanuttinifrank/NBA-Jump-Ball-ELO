import pandas as pd
from bs4 import BeautifulSoup
import requests
from elosports.elo import Elo
from datetime import date


def get_jump_ball_data(start_year, end_year, start_month, start_gameid):
	url_base = "https://www.basketball-reference.com"
	month_dict = {1:"January", 2:"February", 3:"March", 4:"April", 5:"May", 6:"June", 7:"July", 8:"August", 9:"September", 10:"October", 11:"November", 12:"December"}

	jump_ball_df = pd.DataFrame(columns=['TEAM1', 'PLAYER_ID1', 'TEAM2', 'PLAYER_ID2', 'FIRST_PLAYER_WIN'])

	checked_month = False
	checked_game = False

	for year in range(start_year,end_year):

		# Get all months the season was played in
		url_general = "https://www.basketball-reference.com/leagues/NBA_"+str(year)+"_games.html"
		raw_data = requests.get(url_general)
		soup_big = BeautifulSoup(raw_data.text, 'html.parser')
		soup_months = soup_big.find_all("div", class_="filter")[0].find_all("a")
		if start_month and not checked_month:
			for i in range(len(soup_months)):
				mo = soup_months[i].text
				if mo == month_dict[start_month]:
					start_month_index = i
					break
		else:
			start_month_index = 0
		checked_month = True
		for month in soup_months[start_month_index:]:
			url_ending = month.get("href")
			url_schedule = url_base + url_ending

			# Loop through each game from each month in chronological order
			raw_data = requests.get(url_schedule)
			soup_big = BeautifulSoup(raw_data.text, 'html.parser')
			soup = soup_big.find_all('tr')
			if start_gameid and not checked_game:
				for i in range(1,len(soup)):
					check_game_id = soup[i].contents[0].get("csk")
					if check_game_id == start_gameid:
						start_gameid_index = i + 1
						break
			else:
				start_gameid_index = 1
			checked_game = True
			for game in soup[start_gameid_index:]:
				game_id = game.contents[0].get("csk")
				if game_id == None:
					game_id = prev_gameid
					continue
				team1 = game.contents[2].get("csk").split(".")[0]
				team2 = game.contents[4].get("csk").split(".")[0]
				
				boxscore_url = "https://www.basketball-reference.com/boxscores/" + game_id + ".html"
				raw_data = requests.get(boxscore_url)
				if raw_data.status_code == 404:
					game_id = prev_gameid
					continue
				soup_big = BeautifulSoup(raw_data.text, 'html.parser')
				team1_table = soup_big.find_all("table", id="box-"+team1+"-game-basic")[0]
				team1_players = [x.get("href").split("/")[-1].split(".")[0] for x in team1_table.find_all("a")]
				team2_table = soup_big.find_all("table", id="box-"+team1+"-game-basic")[0]
				team2_players = [x.get("href").split("/")[-1].split(".")[0] for x in team2_table.find_all("a")]

				# Get list of jump balls in the game
				game_url = "https://www.basketball-reference.com/boxscores/pbp/" + game_id + ".html"
				raw_data = requests.get(game_url)
				soup_big = BeautifulSoup(raw_data.text, 'html.parser')
				game_pbp = soup_big.find_all("td")
				jump_balls = list(filter(None, [play if 'Jump ball' in play.text else None for play in game_pbp]))
				for jb in jump_balls:
					if len(jb.contents) < 5:
						game_id = prev_gameid
						continue
					player1 = jb.contents[1].get("href").split("/")[-1].split(".")[0]
					if player1 in team1_players:
						p1_team = team1
						p2_team = team2
					else:
						p1_team = team2
						p2_team = team1
					player2 = jb.contents[3].get("href").split("/")[-1].split(".")[0]
					poss_player = jb.contents[5].get("href").split("/")[-1].split(".")[0]
					poss_player_tm = team1 if poss_player in team1_players else team2
					win_team = int(poss_player_tm == p1_team)

					d = {'TEAM1': team1, 'PLAYER_ID1': player1, 'TEAM2': team2, 'PLAYER_ID2': player2, 'FIRST_PLAYER_WIN': win_team}
					jump_ball_df = jump_ball_df.append(pd.DataFrame(d, index=[0]))
					prev_gameid = game_id

			print(month.text, year)

	jump_ball_df_end = jump_ball_df.append(pd.DataFrame({'TEAM1': None, 'PLAYER_ID1': None, 'TEAM2': None, 'PLAYER_ID2': None, 'FIRST_PLAYER_WIN': game_id}, index=[0]))
	return jump_ball_df_end


def create_jump_ball_data():
	jump_ball_df_end = get_jump_ball_data(2015, 2021, None, None)
	pd.to_pickle(jump_ball_df_end, "jump_ball_results.pkl")


def update_jump_ball_data():
	# Get location where dataset ended (last gameid)
	jump_ball_df_end = pd.read_pickle("jump_ball_results.pkl")
	last_gameid = jump_ball_df_end.iloc[-1,4]
	jump_ball_df = jump_ball_df_end.iloc[:-1,]

	# Start getting new data from that point, store in new_data
	curr_year = date.today().year
	last_year = int(last_gameid[:4])
	last_month = int(last_gameid[4:6])
	new_data = get_jump_ball_data(last_year, curr_year+1, last_month, last_gameid)
	new_gameid = new_data.iloc[-1,4]
	new_data = new_data.iloc[:-1,]

	# Update elo ratings
	update_elo_league(new_data)

	# Save updated dataframe
	jump_ball_df = jump_ball_df.append(new_data)
	jump_ball_df_end = jump_ball_df.append(pd.DataFrame({'TEAM1': None, 'PLAYER_ID1': None, 'TEAM2': None, 'PLAYER_ID2': None, 'FIRST_PLAYER_WIN': new_gameid}, index=[0]))
	pd.to_pickle(jump_ball_df_end, "jump_ball_results.pkl")


def create_elo_league():
	eloLeague = Elo(k = 40)

	jump_balls = pd.read_pickle("jump_ball_results.pkl")
	jump_balls = jump_balls.iloc[:-1,]

	for i in range(jump_balls.shape[0]):
		t1, p1, t2, p2, win1 = jump_balls.iloc[i,:]

		# Add players to dict if not yet seen
		if p1 not in eloLeague.ratingDict:
			eloLeague.addPlayer(p1, rating=1500)
		if p2 not in eloLeague.ratingDict:
			eloLeague.addPlayer(p2, rating=1500)

		# Update rankings
		winner = win1 * p1 + (1 - win1) * p2
		loser = win1 * p2 + (1 - win1) * p1
		eloLeague.gameOver(winner, loser, None)

	# Save dict
	pd.to_pickle(eloLeague.ratingDict, "jump_ball_ratings_dict.pkl")


def update_elo_league(new_data):
	ratings_dict = pd.read_pickle("jump_ball_ratings_dict.pkl")
	eloLeague = Elo(k = 40)
	eloLeague.ratingDict = ratings_dict

	for i in range(new_data.shape[0]):
		t1, p1, t2, p2, win1 = new_data.iloc[i,:]

		# Add players to dict if not yet seen
		if p1 not in eloLeague.ratingDict:
			eloLeague.addPlayer(p1, rating=1500)
		if p2 not in eloLeague.ratingDict:
			eloLeague.addPlayer(p2, rating=1500)

		# Update rankings
		winner = win1 * p1 + (1 - win1) * p2
		loser = win1 * p2 + (1 - win1) * p1
		eloLeague.gameOver(winner, loser, None)

	# Save dict
	pd.to_pickle(eloLeague.ratingDict, "jump_ball_ratings_dict.pkl")



if __name__ == '__main__':
	# create_jump_ball_data()
	# create_elo_league()

	update_jump_ball_data()



