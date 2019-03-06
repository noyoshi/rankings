#!/usr/bin/env python3

import json
from flask import Flask, render_template, url_for, request

from elo import Player, update_ratings, get_probs, update_team

# NOTE: THIS IS NOT THREAD SAFE - FOR SMALL SCALE ONLY

app = Flask(__name__)

# Use this to change when you use the app! Can be for more than just ping pong
with open("names.csv", "r") as f:
    name_list = f.read().strip().split(',')

PLAYERS = { name: Player(name) for name in name_list }
MATCHES = []

# Initialize 3 players to start out
PLAYERS["noah"].played = True
PLAYERS["nick"].played = True
PLAYERS["chanhee"].played = True
PLAYERS["allen"].played = True

BEER = { name: Player(name) for name in name_list }
BEER["jack"].played = True
BEER["noah"].played = True
BEER["allen"].played = True
BEERMATCHES = []

def get_sorted_players(PLAYERS, only_active_players=True):
    initial_list = list(PLAYERS.values())
    initial_list.sort(key=lambda x: x.elo, reverse=True)

    # Only get the players who are "active" - played at least 1 match
    if only_active_players:
        player_list = [p for p in initial_list if p.played]
    else:
        player_list = initial_list
    
    # Resets the rankings
    for player in player_list:
        player.champ = False
        player.second = False
        player.third = False
    
    # Update who is now the champion!
    player_list[0].champ = True
    player_list[1].second = True
    player_list[2].third = True
    
    payload = [
        {   
            "name": player.name,
            "elo": int(round(player.elo, 0)),
            "rank": i,
            "output": player.make_output(i)
        }
        for i, player in enumerate(player_list)
    ]
    return payload

def make_dump(PLAYERS):
    return json.dumps([p.dump() for p in PLAYERS.values()])

@app.route("/")
def index():
    return render_template("content.html", players=get_sorted_players(PLAYERS)[0:10])

@app.route("/beer")
def beer():
    return render_template("beer_content.html", players=get_sorted_players(BEER)[0:10])

@app.route("/assets/particles.json")
def particles():
    with open("assets/particles.json", "r") as f:
        d = json.loads(f.read())
    
    return json.dumps(d)

@app.route("/all")
def all1():
    return render_template("content.html", players=get_sorted_players(PLAYERS))

@app.route("/all1")
def all():
    return render_template("beer_content.html", players=get_sorted_players(BEER))

@app.route("/export")
def export():
    return make_dump(PLAYERS)

@app.route("/update", methods=["POST"])
def update():
    # Assume that p0 beat p1
    p0 = request.form.get("p0").strip().lower()
    p1 = request.form.get("p1").strip().lower()
    s0 = int(request.form.get("s0").strip())
    s1 = int(request.form.get("s1").strip())

    for p in p0, p1:
        if p not in PLAYERS:
            PLAYERS[p] = Player(p)
    player0 = PLAYERS[p0]
    player1 = PLAYERS[p1]

    # Updates the elo rating of both players
    update_ratings(player0, player1, (s0, s1))

    # Update the matches list
    MATCHES.append((player0.name, player1.name, (s0, s1)))

    # Don't do this if the project grows...
    with open("backup", "w") as output_file:
        output_file.write(make_dump(PLAYERS))
    
    # Saves the match data as well
    with open("matches-backup", "w") as output_file:
        output_file.write(json.dumps(MATCHES))

    return json.dumps(get_sorted_players(PLAYERS))

@app.route("/beerUpdate", methods=["POST"])
def update_beer():
    p00 = request.form.get("p00").strip().lower()
    p01 = request.form.get("p01").strip().lower()

    p10 = request.form.get("p10").strip().lower()
    p11 = request.form.get("p11").strip().lower()
    
    s0 = int(request.form.get("s0").strip())
    s1 = int(request.form.get("s1").strip())

    for p in p00, p01, p10, p11:
        if p not in BEER:
            BEER[p] = Player(p)

    player00 = BEER[p00]
    player01 = BEER[p01]

    player10 = BEER[p10]
    player11 = BEER[p11]

    team0 = (player00, player01)
    team1 = (player10, player11)
    score = (s0, s1)
    # Updates the elo rating of both players
    update_team(team0, team1, score)

    # Update the matches list
    BEERMATCHES.append(((player00.name, player01.name), (player01.name, player11.name), (s0, s1)))

    # Don't do this if the project grows...
    with open("backup-beer", "w") as output_file:
        output_file.write(make_dump(BEER))
    
    # Saves the match data as well
    with open("matches-backup-beer", "w") as output_file:
        output_file.write(json.dumps(BEERMATCHES))

    return json.dumps(get_sorted_players(BEER))

if __name__ == '__main__':
    app.run(host="0.0.0.0")
    # app.run(
    #     host="noahyoshida.dev", 
    #     port=443,
    #     ssl_context=("", ")
    # )
