from req import RequestHandler
from req import reqenv
from req import Service
import time

class PaperService:
    def __init__(self, db):
        self.db = db
        PaperService.inst = self

    def login(self, email, password):
        cur = yield self.db.cursor()
        yield cur.execute('SELECT "account"."uid" FROM "account" WHERE "account"."email" = %s',
                (email,))
        if cur.rowcount != 1:
            return ('Eaccount', None)
        uid = str(cur.fetchone()[0])
        if uid == password:
            return (None, uid)
        return ('Elogin', None)

class PaperHandler(RequestHandler):
    @reqenv
    def get(self):
        self.render('../http/paper.html',acct=self.acct)
        return

    @reqenv
    def post(self):
        req = str(self.get_argument('req'))
        if req == 'login':
            email = self.get_argument('email')
            password = self.get_argument('password')
            err, uid = yield from PaperService.inst.login(email, password)
            if err:
                self.finish(err)
                return
            self.set_secure_cookie('uid', str(uid), httponly=True, expires=time.time()+3600)
            self.finish('S')
        pass
