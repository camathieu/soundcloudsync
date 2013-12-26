import Sysaccess
import re

class Tracks:
    def __init__(self,controller):
        self.store = {}
        self.controller = controller

    def __getitem__(self,id):
        if id in self.store:
            return self.store[id]
        obj = Sysaccess.rget(self.controller.redis,'track'+str(id))
        if obj:
            self.store[id] = obj
            return self.store[id]
        else:
            self.store[id] = Track(id)
            return self.store[id]

    def __setitem__(self,id,res):
        if id in self.store:
            self.store[id].load(res)
        else:
            self[id]

    def __delitem__(self,id):
        if id in self.store:
            del self.store[id]
            Sysaccess.rdelete(self.controller.redis,'track'+str(id))

import CustomResource
class Track(CustomResource.CustomResource):
    def __init__(self,id):
        CustomResource.CustomResource.__init__(self,id)
	self.favorites = []
        self.playlist_name = None
        self.load()

    def load(self,res=None):
        if not res:
            self.load_res(Track.controller.api.get('/tracks/' + str(self.id)))
        else :
            self.load_res(res)
        self.reload()
        self.save()

    def reload(self):
        if Sysaccess.is_older(self.timestamp,Track.controller.settings.misc['refresh']):
            if self.download():
                self.tag()
            self.timestamp = Sysaccess.now()

    def save(self):
        Sysaccess.rsave(Track.controller.redis,'track'+str(self.id),self)
    
    def filename(self):
        file_name = self.ascii('title')
        if file_name:
            return re.sub("[^\w]+",'_',self.ascii('title')) + ".mp3"
        return False

    def path(self):
        file_name = self.filename()
        if file_name:
            return Track.controller.users[self['user_id']].path() + "/" + file_name 
        return False

    def old_path(self):
        file_name = self.filename()
        if file_name:
            return Track.controller.users[self['user_id']].old_path() + "/" + file_name
        return False

    def artwork_path(self):
        return Track.controller.settings.path['track_artwork'] + "/" + str(self['id']) + ".png"
        
    def get_download_url(self):
        if self['stream_url']:
            url = Track.controller.api.get(self['stream_url'], allow_redirects=False)
            if url and url.location:
                return url.location
        print "download url not found"
        return False

    def download(self):
        if Sysaccess.isfile(self.path()):
            return True

        print "Downloading " + self.ascii('title')
        url = self.get_download_url()
        if not url:
            return False
        success = Sysaccess.download(url,self.path())
        if not success:
            return False
        Sysaccess.clean_tags(self.path())

    def download_artwork(self):
        if Sysaccess.isfile(self.artwork_path()):
            return self.artwork_path()
        url = self['artwork_url']
        if not url:
            return False
        url = re.sub("large","crop",url)
        success = Sysaccess.download(url,self.artwork_path())
        if not success:
            return False
        return self.artwork_path()

    def tag(self,force=False):
        tags = Sysaccess.get_tags(self.path())
        if not tags:
            return False

        new_tags = {}
        if self['title']:
            title = unicode(self.utf8('title').decode('utf-8'))
            if title and tags['TIT2'] != title:
                new_tags['TIT2'] =  unicode(self.utf8('title').decode('utf-8'))
        
        user = Track.controller.users[self['user_id']]
        if user:
            artist = unicode(user.utf8('username').decode('utf-8'))
            if tags['TPE1'] != artist:
                new_tags['TPE1'] = artist

        if self.playlist_name:
            album = unicode(self.playlist_name.decode('utf-8'))
            if not tags['TALB']:
                new_tags['TALB'] = album

        if self['label_name']:        
            label = unicode(self.utf8('label_name').decode('utf-8'))
            if label and tags['TIT1'] != label:
                    new_tags['TIT1'] = label
       
        if self['release_year']: 
            year = unicode(str(self.utf8('release_year')))
            if year and str(tags['TDRC']) !=str( year ):
                new_tags['TDRC'] =  year
       
        if self['description']: 
            desc = unicode(self.utf8('description').decode('utf-8'))
            if desc and tags['COMM'] != desc:
                new_tags['COMM'] = desc

        if self['genre']:
            genre = unicode(self.utf8('genre').decode('utf-8'))
            if genre and tags['TCON'] != genre:
                new_tags['TCON'] = genre
        
        if not tags['APIC']:
            artwork = self.download_artwork()
            if artwork:
                new_tags['APIC'] = artwork

        fav = unicode('##FAV##')
        if self['user_favorite'] and not tags['TCOM'] == fav:
            new_tags['TCOM'] = fav
        elif not self['user_favorite'] and tags['TCOM'] == fav:
            new_tags['TCOM'] = None

        if not len(new_tags.keys()):
            return True

        print "old :" + tags.__repr__()
        print "new :" +  new_tags.__repr__()

        print "taging " + self.utf8('title')
        Sysaccess.tag(self.path(),new_tags)

    def favoritize(self,user):
        if user.id in self.favorites:
	    return True
        
        file_name = self.filename()
        if file_name:
            user_fav_path = user.path() + '/favorites/' + file_name
	print self.path()
	print user_fav_path
        Sysaccess.link(self.path(),user_fav_path)
        if user.id == self.controller.me: 
		self.tag()
        self.favorites.append(user.id)
        self.save()

    def set_playlist(self,playlist_name):
        if not playlist_name:
            return False
        if self.playlist_name == playlist_name:
            return True
        
        file_name = self.filename()
        if file_name:
            playlist_path = Track.controller.users[self['user_id']].path() + '/'+ playlist_name + '/' + file_name 
        Sysaccess.link(self.path(),playlist_path)
        self.playlist_name = playlist_name
        self.tag()
        self.save()

    def __repr__(self):
        return self.utf8('title')
