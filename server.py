#!/usr/bin/env python3

'''
Friendship ended with Flask, now I use Tornado
'''

import os
import sys

import tornado.ioloop
import tornado.options
import tornado.web

import socket
import logging

from elo import Player


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


class UploadHandler(tornado.web.RequestHandler):
    def get(self, name=None):
        with open("names.csv", "r") as f:
            name_list = f.read().strip().split(',')

        PLAYERS = {name: Player(name) for name in name_list}
        PLAYERS["noah"].played = True
        PLAYERS["nick"].played = True
        PLAYERS["chanhee"].played = True
        PLAYERS["allen"].played = True

        self.render('content.html', **{
            'players': get_sorted_players(PLAYERS)
        })


class RankingApplication(tornado.web.Application):
    def __init__(self, **settings):
        print(settings)
        tornado.web.Application.__init__(self, **settings)

        self.logger = logging.getLogger()
        self.ioloop = tornado.ioloop.IOLoop.instance()
        self.port = '88'
        self.address = '127.0.0.1'

        self.add_handlers('.*', [
            (r'/', UploadHandler)
        ])

    def run(self):
        try:
            self.listen(self.port)
        except socket.error as e:
            self.logger.fatal('Unable to listen on {}:{} = {}'.format(
                self.address, self.port, e))
            sys.exit(1)

        self.ioloop.start()


if __name__ == '__main__':
    tornado.options.define(
        'template_path',
        default=os.path.join(os.path.dirname(__file__), "templates"),
        help='Path to templates')
    tornado.options.define(
        'static_path',
        default=os.path.join(os.path.dirname(__file__), "static"),
        help='Path to static')
    tornado.options.parse_command_line()

    options = tornado.options.options.as_dict()
    rankings = RankingApplication(**options)

    rankings.run()
