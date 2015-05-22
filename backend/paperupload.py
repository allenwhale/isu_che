from req import reqenv
from req import RequestHandler
from req import Service
from mail import MailHandler
import subprocess
from os import mkdir 

class PaperuploadService:
    def __init__(self,db):
        self.db = db
        PaperuploadService.inst = self

    def upload(self, uid, topic, title, author, number, op, affiliation, f, ff):
        if not f or not ff:
            return ('Enofile', None)
        cur = yield self.db.cursor()
        yield cur.execute('SELECT "aid" FROM "abstract" WHERE "uid" = %s;', (uid,))
        if cur.rowcount == 0:#new
            if f == None:
                return ('Enofile', None)
            yield cur.execute('INSERT INTO "abstract" ("uid", "topic", "title", "author", "number", "op", "affiliation") VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING "aid";', (uid, topic, title, author, number, op, affiliation))
            if cur.rowcount != 1:
                return ('EDB', None)
            aid = str(cur.fetchone()[0])
            mkdir('../http/paper/'+str(uid))
            path = '../http/paper/'+str(uid)+'/abs' + aid + '.' + f['filename'].split('.')[-1]
            _f = open(path, 'wb+')
            _f.write(f['body'])
            _f.close()
            path = '../http/paper/'+str(uid)+'/cop' + aid + '.' + ff['filename'].split('.')[-1]
            _f = open(path, 'wb+')
            _f.write(ff['body'])
            _f.close()
            return (None, aid)
        else:#edit
            yield cur.execute('UPDATE "abstract" SET "uid" = %s, "topic" = %s, "title" = %s, "author" = %s, number = %s, "op" = %s, "affiliation" = %s RETURNING "aid";', (uid, topic, title, author, number, op, affiliation))
            if cur.rowcount != 1:
                return ('EDB', None)
            aid = str(cur.fetchone()[0])
            subprocess.call(['rm','-rf','../http/paper/'+str(uid)])
            mkdir('../http/paper/'+str(uid))
            path = '../http/paper/'+str(uid)+'/abs' + aid + '.' + f['filename'].split('.')[-1]
            _f = open(path, 'wb+')
            _f.write(f['body'])
            _f.close()
            path = '../http/paper/'+str(uid)+'/cop' + aid + '.' + ff['filename'].split('.')[-1]
            _f = open(path, 'wb+')
            _f.write(ff['body'])
            _f.close()
            return (None, aid)

    def get_abstract_info(self, uid):
        cur = yield self.db.cursor()
        yield cur.execute('SELECT "aid", "topic", "title", "author", "number", "op", "affiliation" FROM "abstract" WHERE "uid" = %s;', (uid,))
        if cur.rowcount != 1:
            return ('EDB', None)
        meta = cur.fetchone()
        meta = {'aid': str(meta[0]),
                'topic': str(meta[1]),
                'title': str(meta[2]),
                'author': str(meta[3]),
                'number': str(meta[4]),
                'op' : str(meta[5]),
                'affiliation': str(meta[6])
                }
        return (None, meta)
'''
    def upload(self, uid, topic, title, number, keyword, abstract, author):
        cur = yield self.db.cursor()
        yield cur.execute('SELECT "abstract"."aid" FROM "abstract" WHERE "abstract"."uid" = %s ', (uid,))
        if cur.rowcount == 0:
            yield cur.execute('INSERT INTO "abstract" ("uid", "topic", "title", "number", "abstract") '
                    'VALUES (%s, %s, %s, %s, %s) RETURNING "abstract"."aid";', (uid, topic, title, number, abstract))
            if cur.rowcount != 1:
                return ('EDB',  None)
            aid = str(cur.fetchone()[0])
            err, aid = self.upload_keyword(aid, keyword)
            if err:
                return (err, None)
            err, aid = self.upload_author(aid, author)
            if err:
                return (err, None)
            return (None, aid)
        else:
            aid = str(cur.fetchone()[0])
            yield cur.execute('UPDATE "abstract" SET ("uid", "topic", "title", "number", "abstract") = '
                    '(%s, %s, %s, %s, %s) WHERE "abstract"."aid" = %s;', (uid, topic, title, number, abstract, aid))
            if cur.rowcount != 1:
                return ('EDB', None)
            err, aid = yield from self.upload_keyword(aid, keyword)
            if err:
                return (err, None)
            err, aid = yield from self.upload_author(aid, author)
            if err:
                return (err, None)
            return (None, aid)


    def upload_author(self, aid, author):
        cur = yield self.db.cursor()
        yield cur.execute('DELETE FROM "author_of_abstract" WHERE "author_of_abstract"."aid" = %s;', (aid,))
        for a in author:
            yield cur.execute('INSERT INTO "author_of_abstract" ("aid", "first_name", "last_name", "position", '
                    '"department", "affiliation","addition", "email") '
                    'VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING "author_of_abstract"."auid";', (aid,)+a)
            if cur.rowcount != 1:
                return ('EDB', None)
        return (None, aid)

    def upload_keyword(self, aid, keyword):
        cur = yield self.db.cursor()
        yield cur.execute('DELETE FROM "keyword_of_abstract" WHERE "keyword_of_abstract"."aid" = %s', (aid,))
        for k in keyword:
            yield cur.execute('INSERT INTO "keyword_of_abstract" ("aid", "keyword") '
                    'VALUES (%s, %s) RETURNING "keyword_of_abstract"."kid";', (aid, k))
            if cur.rowcount != 1:
                return ('EDB', None)
        return (None, aid)
    def get_abstract_info(self, uid):
        cur = yield self.db.cursor()
        yield cur.execute('SELECT "abstract"."aid" ,"abstract"."topic", "abstract"."title", "abstract"."number", "abstract"."abstract" '
                'FROM "abstract" WHERE "abstract"."uid" = %s;', (uid,))
        if cur.rowcount != 1:
            return (None, None)
        res = {}
        (aid, topic, title, number, abstract) = cur.fetchone()
        res['aid'] = aid
        res['topic'] = topic
        res['title'] = title
        res['number'] = number
        res['abstract'] = abstract
        res['keyword'] = yield from self.get_keyword_info(aid)
        res['author'] = yield from self.get_author_info(aid)
        return (None, res)

    def get_author_info(self, aid):
        cur = yield self.db.cursor()
        yield cur.execute('SELECT "author_of_abstract"."first_name", "author_of_abstract"."last_name", '
                '"author_of_abstract"."position", "author_of_abstract"."department", "author_of_abstract"."affiliation", '
                '"author_of_abstract"."addition", "author_of_abstract"."email" '
                'FROM "author_of_abstract" WHERE "author_of_abstract"."aid" = %s;', (aid, ))
        res = []
        for (first_name, last_name, position, department, affiliation, addition, email) in cur:
            res.append({
                'first_name': first_name,
                'last_name': last_name,
                'position': position,
                'department': department,
                'affiliation': affiliation,
                'addition': addition,
                'email': email})
        return res

    def get_keyword_info(self, aid):
        cur = yield self.db.cursor()
        yield cur.execute('SELECT "keyword_of_abstract"."keyword" FROM "keyword_of_abstract" '
                'WHERE "keyword_of_abstract"."aid" = %s;', (aid,))
        res = []
        for (k,) in cur:
            res.append(k)
        return res
'''


class PaperuploadHandler(RequestHandler):
    @reqenv
    def get(self):
        uid = self.get_secure_cookie('uid')
        if not uid:
            self.redirect('/paper#/third')
            return
        uid = str(int(uid))
        err, abstract = yield from PaperuploadService.inst.get_abstract_info(uid)
        #abstract = None
        self.render('../http/paperupload_2.html',acct=self.acct, abstract=abstract)
        return

    '''@reqenv
    def post(self):
        uid = self.get_secure_cookie('uid')
        if not uid:
            self.finish('Elogin')
            return
        uid = str(int(uid))
        topic = str(self.get_argument('topic'))
        title = str(self.get_argument('title'))
        number = str(self.get_argument('number'))
        abstract = str(self.get_argument('abstract'))
        keyword = self.get_arguments('keyword[]')
        first_name = self.get_arguments('first_name[]')
        last_name = self.get_arguments('last_name[]')
        position = self.get_arguments('position[]')
        department = self.get_arguments('department[]')
        affiliation = self.get_arguments('affiliation[]')
        addition = self.get_arguments('addition[]')
        email = self.get_arguments('email[]')
        author = zip(list(first_name), list(last_name), list(position), list(department), list(affiliation), list(addition), list(email))
        err, aid = yield from PaperuploadService.inst.upload(uid, topic, title, number, keyword, abstract, author)
        if err:
            self.finish(err)
            return
        self.clear_cookie('uid')
        self.finish(str(aid))'''

    @reqenv
    def post(self):
        uid = self.get_secure_cookie('uid')
        if not uid:
            self.finish('Elogin')
            return
        uid = str(int(uid))
        topic = str(self.get_argument('topic'))
        title = str(self.get_argument('title'))
        op = str(self.get_argument('op'))
        affiliation = self.get_argument('affiliation')
        author = str(self.get_argument('author'))
        number = str(self.get_argument('number'))
        print('uid',uid)
        try:
            f1 = self.request.files['attach'][0]
            f2 = self.request.files['copyright'][0]
        except:
            f1 = None
            f2 = None
        err, aid = yield from PaperuploadService.inst.upload(uid, topic, title, author, number, op, affiliation, f1, f2)
        if err:
            self.finish(err)
            return
        err, meta = yield from Service.User.get_acct_meta(uid)
        m = MailHandler('../http/abstract_mail.html')
        m.send(to=meta['email'],subject='台灣化學工程學會62nd年會 摘要投稿通知!!',title=title,topic=topic,name=author)
        self.render('../http/afterabs.html',name=author,title=title,topic=topic)
        return
