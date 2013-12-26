import soundcloud

class Api:
        
    def __init__(self,controller,user,password):
        self.controller = controller
        
        self.sc = self.connect(user,password)

    def connect(self,user,password):
        client = soundcloud.Client(
            client_id="your soundcloud client id",
            client_secret="your soundcloud client secret",
            username=user,
            password=password
        )
        return client

    def get(self,resource,**kwargs):
        try:
            return self.sc.get(resource,**kwargs)
        except Exception,e:
            print e
            return False       

    def getAll(self,resource):
        limit = 100
        offset = 0
        res_list = []
        while True:
            fetch = self.get(resource,limit=limit,offset=offset)
            if not fetch or not fetch.__class__.__name__ == 'ResourceList':
                return False
            
            for res in fetch:
                res_list.append(res);
            offset = offset + limit
            if len(fetch) < limit:
                return res_list
