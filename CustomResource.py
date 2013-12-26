import time

class CustomResource:

    controller = None

    def __init__(self,id):
        self.id = id
        self.res = None
        self.timestamp = 0
 
    def load_res(self,res):
        self.res = {}
        for key in res.obj.keys():
            self.res[str(key)] = res.obj[key]

    def __getitem__(self,key):
        if not self.res:
            print "Object is not initialized"
            return False
        if self.res and key in self.res.keys():
            return self.res[key]
        return False

    def utf8(self,key):
        if key in self.res.keys():
            value = self.res[key]
            if not value:
                return False
            if value.__class__.__name__ == "unicode":
                return value.encode("utf-8","ignore")
            else:
                return value

    def ascii(self,key):
        if key in self.res.keys():
            value = self.res[key]
            if not value:
                return False
            if value.__class__.__name__ == "unicode":
                return value.encode("ascii","ignore")
            else:
                return value
