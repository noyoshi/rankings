'''
Friendship ended with Flask, now I use Tornado
'''
import tornado.ioloop
import tornado.options
import tornado.web

import socket
import logging

import os
import sys

class UploadHandler(tornado.web.RequestHandler):
    def get(self, name=None):
        print(name)

        self.render('paste.tmpl')

class RankingApplication(tornado.web.Application):
    def __init__(self, **settings):
        tornado.web.Application.__init__(self, **settings)

        self.logger   = logging.getLogger()
        self.ioloop = tornado.ioloop.IOLoop.instance()
        self.address = "localhost"
        self.port = '88'

        self.add_handlers('.*', [
            (r'.*/(.*)' , UploadHandler)
        ])

    def run(self):
        try:
            self.listen(self.port)
        except socket.error as e:
            self.logger.fatal('Unable to listen on {}:{} = {}'.format(self.address, self.port, e))
            sys.exit(1)

        self.ioloop.start()

if __name__ == '__main__':
    tornado.options.define(
        'template_path', 
        default=os.path.join(os.path.dirname(__file__), "templates"), 
        help='Path to templates')
    tornado.options.parse_command_line()

    options = tornado.options.options.as_dict()
    rankings = RankingApplication(**options)

    rankings.run()
