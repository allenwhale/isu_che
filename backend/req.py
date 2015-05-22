import json
import msgpack
import types
import datetime
import collections
import tornado.template
import tornado.gen
import tornado.web
import tornado.websocket

class Service:
    pass

class RequestHandler(tornado.web.RequestHandler):
    def __init__(self,*args,**kwargs):
        #self.db = kwargs.pop('db')
        #self.rs = kwargs.pop('rs')
        #self.ars = kwargs.pop('ars')
        super().__init__(*args,**kwargs)

        try:
            self.get_argument('json')
            self.res_json = True

        except tornado.web.HTTPError:
            self.res_json = False

    def error(self,err):
        self.finish(err)
        return

    def get_args(self, args):
        meta = {}
        for a in args:
            meta[a] = self.get_argument(a, None)
        return meta
        
    def render(self,templ,**kwargs):
        class _encoder(json.JSONEncoder):
            def default(self,obj):
                if isinstance(obj,datetime.datetime):
                    return obj.isoformat()

                else:
                    return json.JSONEncoder.default(self,obj)

        def _mp_encoder(obj):
            if isinstance(obj,datetime.datetime):
                return obj.isoformat()
            return obj

        if self.res_json == True:
            self.finish(json.dumps(kwargs,cls = _encoder))

        else:
            tpldr = tornado.template.Loader('.')
            data = tpldr.load(templ).generate(**kwargs)
            self.finish(data)

        return

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def __init__(self,*args,**kwargs):
        self.db = kwargs.pop('db')
        self.rs = kwargs.pop('rs')
        self.ars = kwargs.pop('ars')

        super().__init__(*args,**kwargs)

def reqenv(func):
    @tornado.gen.coroutine
    def wrap(self,*args,**kwargs):
        err,acct_id = yield from Service.User.get_sign_info(self)
        err,self.acct = yield from Service.User.get_acct_meta(acct_id)
        try:
            self.admin = self.get_cookie('admin')
        except:
            self.admin = None
        ret = func(self,*args,**kwargs)
        if isinstance(ret,types.GeneratorType):
            ret = yield from ret

        return ret

    return wrap
