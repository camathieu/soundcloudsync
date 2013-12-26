USER = {
    'user'      : "email",
    'password'  : "password",
}

PATH = {
    'data'              : "/home/skatkatt/data/SoundCloud/Sounds",
    'track_artwork'     : "/home/skatkatt/data/SoundCloud/Artwork/Tracks",
    'user_artwork'      : "/home/skatkatt/data/SoundCloud/Artwork/Users",
    'app_data'          : "/home/skatkatt/data/SoundCloud/AppData",
}

MISC = {
    'refresh'       : 60 * 60 * 24,  # 24 Hours Chrono
}

GUESTS = [
        1488            # laurent garnier
]

class Settings:

    def __init__(self,controller):
        self.controller = controller
        self.user = USER
        self.path = PATH
        self.misc = MISC
	self.guests = GUESTS

if __name__ == "__main__" :
    settings = Settings(None)
    print settings.user['user']
