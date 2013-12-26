#!/usr/bin/python

import Settings

import Api

import CustomResource
import Users
import Tracks

import Sysaccess
import redis

class Controller:
    
    def __init__(self):

        CustomResource.CustomResource.controller = self

        self.redis = redis.Redis('localhost')
        self.settings   = Settings.Settings(self)
        self.api        = Api.Api(self,self.settings.user['user'],self.settings.user['password'])

        self.users  = Users.Users(self)
        self.tracks = Tracks.Tracks(self)

        me = self.api.get('/me')
        self.me = me.id
        self.users[me.id] = me
        self.users[me.id].download()

	for guest in self.settings.guests:
		self.users[guest].download()


if __name__ == "__main__":
    c = Controller()

#    print c.users[49299].utf8('username')
#    print c.users[49299].ascii('username')
#    print c.users[49299].path()
