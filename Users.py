import Sysaccess

class Users:
    
    def __init__(self,controller):
        self.store = {}
        self.controller = controller

    def __getitem__(self,id):
        if id in self.store:
            return self.store[id]
        obj = Sysaccess.rget(self.controller.redis,'user'+str(id))
        if obj:
            self.store[id] = obj
            return self.store[id]
        else:
            self.store[id] = User(id)
            return self.store[id]

    def __setitem__(self,id,res):
        if id in self.store:
            self.store[id].load(res)
        else:
            self[id]

    def __delitem__(self,id):
        if id in self.store:
            del self.store[id]
            Sysaccess.rdelete(self.controller.redis,'user'+str(id))

import CustomResource
class User(CustomResource.CustomResource):
    def __init__(self,id):
        CustomResource.CustomResource.__init__(self,id)
        self.load()
    
    def load(self,res=None):
        if not res:
            self.load_res(User.controller.api.get('/users/' + str(self.id)))
        else :
            self.load_res(res)
        self.save()

    def download(self):
        self.playlists()
        self.tracks()
        self.favorites()
        #self.followings()
        self.save()
    
    def save(self):
        Sysaccess.rsave(User.controller.redis,'users'+str(self.id),self)

    def path(self):
        dir_name = self.ascii('permalink')
        if dir_name: 
            return User.controller.settings.path['data'] + "/" + dir_name
        return False

    def old_path(self):
        dir_name = self.ascii('permalink')
        if dir_name:
            return User.controller.settings.path['old_data'] + "/" + dir_name
        return False

    def followings(self):
        if self.id == User.controller.me:
            followings = User.controller.api.getAll('/users/' + str(self['id']) + '/followings')
            if followings:
                print self.utf8('username') + " has " + str(len(followings)) + " followings"
                for following in followings:
                    User.controller.users[following.id].load(following)
                    User.controller.users[following.id].download()
        else:
            return False

    def tracks(self):
        tracks = User.controller.api.getAll('/users/' + str(self['id']) + '/tracks')
        if tracks:
            print self.utf8('username') + " has " + str(len(tracks)) + " tracks"    
            for track in tracks:
                User.controller.tracks[track.id] = track
        else:
            return False

    def favorites(self):
        if self.id == User.controller.me or self.id in User.controller.settings.guests:
            favorites = User.controller.api.getAll('/users/' + str(self['id']) + '/favorites')
            if favorites:
                print self.utf8('username') + " has " + str(len(favorites)) + " favorites"
                for track in favorites:
                    User.controller.tracks[track.id] = track
                    User.controller.tracks[track.id].favoritize(self)
        else:
            return False

    def playlists(self):
        playlists = User.controller.api.getAll('/users/' + str(self['id']) + '/playlists')
        if playlists:
            print self.utf8('username') + " has " + str(len(playlists)) + " playlists"
            for playlist in playlists:
                if playlist.title and len(playlist.tracks):
                    playlist_name = playlist.title.encode("utf-8","ignore")
                    print "playlist " + playlist_name + " has " + str(len(playlist.tracks)) + " tracks"
                    for track in playlist.tracks:    
                        if User.controller.tracks[track['id']]:
                            User.controller.tracks[track['id']].set_playlist(playlist_name)
        else:
            return False

    def __repr__(self):
        return self.utf8('username')
