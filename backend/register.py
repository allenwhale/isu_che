from req import RequestHandler
from req import reqenv
from req import Service
from mail import MailHandler

class RegisterService():
    def __init__(self,db):
        self.db = db
        RegisterService.inst = self

    def register(self, data):
        def gen_sql(data):
            sql1, sql2 = '', ''
            prama = ()
            for d in data:
                if sql1 == '':
                    sql1 = sql1 + ' "%s" '%d
                else:
                    sql1 = sql1 + ' ,"%s" '%d
                if sql2 == '':
                    sql2 = ' %s '
                else:
                    sql2 = sql2 + ' ,%s ' 
                prama = prama+(data[d],)
            sql1 = '( '+sql1+' )'
            sql2 = 'VALUES( '+sql2+' )'
            return (sql1+sql2, prama)


        cur = yield self.db.cursor()
        yield cur.execute('SELECT 1 FROM "register" WHERE "register"."name" = %s;',(data['name'],))
        if cur.rowcount != 0:
            return ('Eexistname',None)
        yield cur.execute('SELECT 1 FROM "register" WHERE "register"."email" = %s;',(data['email'],))
        if cur.rowcount != 0:
            return ('Eexistemail',None)
        sql, prama = gen_sql(data)
        yield cur.execute('INSERT INTO "register" '+sql+' RETURNING "register"."rid";', prama)
        if cur.rowcount != 1:
            return ('EDB',None)
        return (None,cur.fetchone()[0])

    def forget(self, data):
        cur = yield self.db.cursor()
        yield cur.execute('SELECT "rid" FROM "register" WHERE "email" = %s AND "transnum" = %s;', (data['email'], data['transnum']))
        if cur.rowcount != 1:
            return ('Eexist', None)
        uid = cur.fetchone()[0]
        return (None, uid)

class RegisterHandler(RequestHandler):
    @reqenv
    def get(self):
        self.render('../http/register.html',page='register',acct=self.acct)
        return
    @reqenv
    def post(self):
        args = ['email', 'transnum']
        meta = self.get_args(args)
        err, uid = yield from RegisterService.inst.forget(meta)
        if err:
            self.finish(err)
            return
        self.finish(str(uid))
        return

class IndivisualregHandler(RequestHandler):
    @reqenv
    def get(self):
        self.render('../http/indivisualreg.html',acct=self.acct)
        return

    @reqenv
    def post(self):
        args = ['name', 'title', 'affiliation', 'department', 'address', 'email', 'phone', 'package', 'banquet', 'total', 'food', 'paper', 'transnum', 'invoice', 'vat']
        meta = self.get_args(args)
        if not meta['food']:
            meta['food'] = -1
        err,rid = yield from RegisterService.inst.register(meta)
        if err:
            self.finish(err)
            return
        m = MailHandler('../http/register_mail.html')
        m.send(to=meta['email'], subject='台灣化學工程學會62th年會報名確認', _from='TwIChE@isu.edu.tw', rid='%04d'%rid, name=meta['name'])
        self.render('../http/afterreg.html', rid='%04d'%rid, name=meta['name'])
        return
