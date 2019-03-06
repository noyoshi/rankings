import collections

def get_probs(player0, player1):
    p0 = (1.0 / (1.0 + pow(10, ((player0.elo - player1.elo) / 400))))
    p1 = (1.0 / (1.0 + pow(10, ((player1.elo - player0.elo) / 400))))
    return p0, p1

def update_ratings(player0, player1, score):
    # Assume that player0 won
    K = 30
    p0, p1 = get_probs(player0, player1)
    
    # Generates ELO
    player0.elo = player0.elo + (K * (1 - p0))
    player1.elo = player1.elo + (K * (0 - p1))

    # Updates the games played
    player0.total_games += 1
    player1.total_games += 1

    # Update the history - show that player0 beat player1
    player0.past_games[player1.name].append((1, score))
    player1.past_games[player0.name].append((0, score))

    # Indicate that these players have played at least one game
    player0.played = True
    player1.played = True

def update_team(team0, team1, score):
    K = 30
    team0_elo = (team0[0].elo + team0[1].elo) / 2
    team1_elo = (team1[0].elo + team1[1].elo) / 2
    p0 = (1.0 / (1.0 + pow(10, ((team0_elo - team1_elo) / 400))))
    p1 = (1.0 / (1.0 + pow(10, ((team1_elo - team0_elo) / 400))))
    team0[0].elo = team0[0].elo + (K * (1 - p0))
    team0[1].elo = team0[1].elo + (K * (1 - p0))

    team1[0].elo = team1[0].elo + (K * (0 - p1))
    team1[1].elo = team1[1].elo + (K * (0 - p1))

    for player in team0:
        player.played = True
    
    for player in team1:
        player.played = True

class Player(object):
    def __init__(self, name):
        self.name = name
        self.total_games = 0
        self.elo = 1000
        self.past_games = collections.defaultdict(list)
        self.champ = False
        self.second = False
        self.third = False
        self.played = False

    def __str__(self):
        return "{},{}".format(self.name, round(self.elo, 2))
    
    def make_output(self, rank):
        """Gets a custom emoji output!"""
        modifier = ""
        if self.champ:
            modifier = " 👑"
        elif self.second:
            modifier = " 🥈"
        elif self.third:
            modifier = " 🥉"
        return str(rank + 1) + modifier

    def dump(self):
        return self.name, self.total_games, self.elo
    
    def full_dump(self):
        return self.name, self.total_games, self.elo, self.past_games

if __name__ == '__main__':
    noah = Player("noah")
    nick = Player("nick")
    update_ratings(noah, nick, (12, 0))
    update_ratings(noah, nick, (11, 10))
    print(noah)
    print(nick)


