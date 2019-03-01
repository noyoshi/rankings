#!/usr/bin/env python3

import json
from flask import Flask, render_template, url_for, request

from elo import Player, update_ratings, get_probs

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

def get_sorted_players(only_active_players=True):
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
    return render_template("content.html", players=get_sorted_players()[0:10])

@app.route("/all")
def all():
    return render_template("content.html", players=get_sorted_players())

@app.route("/export")
def export():
    return make_dump(PLAYERS)

@app.route("/update", methods=["POST"])
def update():
    # Assume that p0 beat p1
    p0 = request.form.get("p0").strip()
    p1 = request.form.get("p1").strip()
    s0 = int(request.form.get("s0").strip())
    s1 = int(request.form.get("s1").strip())

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

    return json.dumps(get_sorted_players())

if __name__ == '__main__':
    app.run(host="0.0.0.0")
