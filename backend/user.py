from req import RequestHandler
from req import reqenv
from req import Service
class UserService:
    def __init__(self,db):
        self.db = db
        self.MOD = 1000000007
        self.C = 131
        self.ORGIN = self.MOD - 1
        UserService.inst = self 

    def _hash(self,pwd):
        res = self.ORGIN
        for s in pwd:
            res = (res * self.C + ord(s)) % self.MOD
        return res

    def signup(self,email,name,place,title,pwd):
        cur = yield self.db.cursor()
        yield cur.execute('SELECT "account"."uid" FROM "account" '
                'WHERE "account"."email" = %s;',(email,))
        if cur.rowcount != 0 :
            return ('Eexistemail',None)
        yield cur.execute('SELECT "account"."uid" FROM "account" '
                'WHERE "account"."name" = %s;',(name,))
        if cur.rowcount != 0 :
            return ('Eexistname',None)
        yield cur.execute('INSERT INTO "account" '
                '("email","name","place","title","password") '
                'VALUES(%s,%s,%s,%s,%s) RETURNING "account"."uid";',
                (email,name,place,title,str(self._hash(pwd))))
        if cur.rowcount != 1:
            return ('EDB',None)
        return (None,cur.fetchone()[0])

    def signin(self,email,pwd):
        cur = yield self.db.cursor()
        yield cur.execute('SELECT "account"."password","account"."uid" '
                'FROM "account" WHERE "account"."email" = %s;',(email,))
        if cur.rowcount != 1:
            return ('Enoexist',None)
        meta = cur.fetchone()
        if(str(self._hash(pwd)) != str(meta[0])):
            return ('Epwderror',None)
        return (None,int(meta[1]))

    def get_acct_meta(self,uid):
        if uid == 0:
            meta = {'uid':0,'name':'','email':'','place':'','title':''}
            return (None,meta) 
        cur = yield self.db.cursor()
        yield cur.execute('SELECT "account"."name","account"."email",'
                '"account"."place","account"."title" '
                'FROM "account" WHERE "account"."uid" = %s',(uid,))
        if cur.rowcount != 1:
            return ('EDB',None)
        meta = cur.fetchone()
        meta = {'uid':uid,
                'name':meta[0],
                'email':meta[1],
                'place':meta[2],
                'title':meta[3]}
        return (None,meta)

    def get_sign_info(self,req):
        try:
            acct_id = int(req.get_secure_cookie('uid'))
        except:
            acct_id = 0
            return (None,acct_id)
        cur = yield self.db.cursor()
        yield cur.execute('SELECT 1 FROM "account" '
                'WHERE "account"."uid" = %s;',(acct_id,))
        if cur.rowcount != 1:
            return ('Esign',None)
        return (None,acct_id)

class SignupHandler(RequestHandler):
    @reqenv
    def get(self):
        self.render('../http/signup.html',page='signup',acct = self.acct)
        return
    @reqenv
    def post(self):
        email = str(self.get_argument('email'))
        name = str(self.get_argument('name'))
        place = str(self.get_argument('place'))
        title = str(self.get_argument('title'))
        pwd = str(self.get_argument('pwd'))
        err,uid = yield from UserService.inst.signup(email,name,place,title,pwd)
        if(err):
            self.finish(err)
            return
        self.finish(str(uid))
        return

class SigninHandler(RequestHandler):
    @reqenv
    def get(self):
        if self.acct['uid'] != 0:
            self.redirect('/')
            return
        self.render('../http/signin.html',page='signin',acct = self.acct)
        return

    @reqenv
    def post(self):
        if self.acct['uid'] != 0:
            return

        email = str(self.get_argument('email'))
        pwd = str(self.get_argument('password'))
        err,uid = yield from UserService.inst.signin(email,pwd)
        if err:
            self.finish(err)
            return
        self.set_secure_cookie('uid',str(uid),path='/',httponly=True)
        self.finish(str(uid))
        return 

class LogoutHandler(RequestHandler):
    @reqenv
    def get(self):
        self.clear_cookie('uid')
        self.redirect('/')
        return
    def post(self):
        self.clear_cookie('uid')
        return
