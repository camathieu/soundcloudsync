import os, sys, signal, shutil, errno
import cPickle as Pickle
import redis
import urllib, hashlib
import time, datetime
import mutagen.id3

def rsave(redis, key, value):
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    str = Pickle.dumps(value)
    redis.set(key,str)
    signal.signal(signal.SIGINT, signal.SIG_DFL)

def rget(redis,key):
    str = redis.get(key)
    if str:
        try:
            object = Pickle.loads(str)
            return object
        except:
            print "fail removing" + key
            redis.delete(key)
    return False

def rdelete(redis,key):
    redis.delete(key)

def now():
    return int(time.time())

def is_older(time,delta):
    if now() - time > delta:
        return True
    return False

def isfile(path):
    return os.path.isfile(path)

def move(old_path,new_path):
    if not isfile(old_path):
        return False

    dir,filename = os.path.split(new_path)
    if not os.path.isdir(dir):
        os.makedirs(dir)

    shutil.move(old_path,new_path)
    return True

def link(source,dest):
    if not isfile(source):
        return False
    if isfile(dest):
        return False

    dir,filename = os.path.split(dest)
    if not os.path.isdir(dir):
        os.makedirs(dir)

    try:
    	os.symlink(source,dest)
    except OSError, e:
        if e.errno == errno.EEXIST:
            os.remove(dest)
            os.symlink(source,dest)
    return True

def download(url,path):
    def hook(*data):
        file_size = int(data[2]/1000)
        total_packets = data[2]/data[1]
        downloaded_packets = data[0]
        sys.stdout.write("\rDownload size\t= %i ko, packet: %i/%i" % (file_size, downloaded_packets, total_packets+1))
        sys.stdout.flush()

    def computeHash(path):
        fh = open(path, 'rb')
        m = hashlib.md5()
        while True:
            data = fh.read(8192)
            if not data:
                break
            m.update(data)
        return m.hexdigest()

    def computeSize(path):
        size =  os.path.getsize(path)
        for unit in ['bytes','KB','MB','GB','TB']:
            if size < 1024.0:
                return "%3.1f %s" % (size, unit)
            size /= 1024.0

    dir,filename = os.path.split(path)
    if not os.path.isdir(dir):
        os.makedirs(dir)

    start = now()

    print ""
    print "DOWNLOADING : " + path
    print ""

    try:
        urllib.urlretrieve(url, path, hook)
    except Exception, e:
        print e
        return False

    time = now() - start
    md5 = computeHash(path)
    size = computeSize(path)

    print ""
    print "SUCCESS : Time = " + str(datetime.timedelta(seconds=time)) + ", Size = " + str(size) + ", MD5SUM = " + str(md5)
    print ""


    return {
        'time'  : time ,
        'md5'   : md5 ,
        'size'  : size ,
    }

def clean_tags(path):
    if not isfile(path):
        return False
    mutagen.id3.delete(path,True,True)

def get_tags(path):
    if not isfile(path):
        return False

    try:
        audio = mutagen.id3.ID3(path)
    except mutagen.id3.ID3NoHeaderError:
        audio = mutagen.id3.ID3()

    tags = {}

    #Title
    if 'TIT2' in audio.keys():
        tags['TIT2'] = audio['TIT2'].text[0]
    else:
        tags['TIT2'] = None

    #Artist
    if 'TPE1' in audio.keys():
        tags['TPE1'] = audio['TPE1'].text[0]
    else:
        tags['TPE1'] = None

    #Album
    if 'TALB' in audio.keys():
        tags['TALB'] = audio['TALB'].text[0]
    else:
        tags['TALB'] = None

    #Comment
    if "COMM::'eng'" in audio.keys():
        tags["COMM"] = audio["COMM::'eng'"].text[0]
    else:
        tags['COMM'] = None

    #Label
    if 'TIT1' in audio.keys():
        tags['TIT1'] = audio['TIT1'].text[0]
    else:
        tags['TIT1'] = None
    
    #YEAR
    if 'TDRC' in audio.keys():
        tags['TDRC'] = audio['TDRC'].text[0]
    else:
        tags['TDRC'] = None
   
    #Style
    if 'TCON' in audio.keys():
        tags['TCON'] = audio['TCON'].text[0]
    else:
        tags['TCON'] = None

    #Composer(fav)
    if 'TCOM' in audio.keys():
        tags['TCOM'] = audio['TCOM'].text[0]
    else:
        tags['TCOM'] = None
    
    #Picture
    if 'APIC:' in audio.keys() or 'APIC:Artwork' in audio.keys():
        tags['APIC'] = True
    else:
        tags['APIC'] = None
    return tags

def tag(path,tags):
    if not isfile(path):
        return False
   
    # WRITE TAGS
    try:
        audio = mutagen.id3.ID3(path)
    except mutagen.id3.ID3NoHeaderError:
        audio = mutagen.id3.ID3()
 
    if 'TIT2' in tags.keys():
        audio['TIT2'] = mutagen.id3.TIT2(encoding=3, text= tags['TIT2'] )
    if 'TPE1' in tags.keys():
        audio['TPE1'] = mutagen.id3.TPE1(encoding=3, text= tags['TPE1'] )
    if 'TALB' in tags.keys():
        audio['TALB'] = mutagen.id3.TALB(encoding=3, text= tags['TALB'] )
    if 'TIT1' in tags.keys():
        audio['TIT1'] = mutagen.id3.TIT1(encoding=3, text= tags['TIT1'] )
    if 'TDRC' in tags.keys():
        audio['TDRC'] = mutagen.id3.TDRC(encoding=3, text= tags['TDRC'] )
    if 'TCON' in tags.keys():
        audio['TCON'] = mutagen.id3.TCON(encoding=3, text= tags['TCON'] )
    if 'TCOM' in tags.keys():
        audio['TCOM'] = mutagen.id3.TCOM(encoding=3, text= tags['TCOM'] )
    if 'COMM' in tags.keys():
        audio['COMM'] = mutagen.id3.COMM(encoding=3, text= tags['COMM'] , desc = '', lang= unicode('eng') ) 
    if 'APIC' in tags.keys() and isfile(tags['APIC']) :
        audio['APIC'] = mutagen.id3.APIC(encoding=3, mime="image/jpeg", type=3, desc=unicode('Artwork'), data=open(tags['APIC']).read())

    audio.save(path)

if __name__ == '__main__':
    path = "/home/skatkatt/data/SoundCloud/Sounds/dirtysouth/Dirty South - Listen Again/Dirty_South_Live_Green_Valley_Festival_Brazil_29th_Jan_2011.mp3"
    print get_tags(path)
