from req import reqenv
from req import RequestHandler
from req import Service

class PaperuploadService:
    def __init__(self,db):
        self.db = db
        PaperuploadService.inst = self

    def upload(self,rid,name,theme,competition,title,author,affiliation,number,f):
        cur = yield self.db.cursor()
        yield cur.execute('SELECT 1 FROM "paper" WHERE "paper"."rid" = %s;',(rid,))
        if cur.rowcount != 0:
            return('Eexist',None)
        yield cur.execute('SELECT 1 FROM "register" WHERE "register"."rid" = %s;',(rid,))
        if cur.rowcount != 1:
            return ('Enoexist',None)
        yield cur.execute('INSERT INTO "paper" ("rid","name","theme","competition",'
                '"title","author","affiliation","number") '
                'VALUES(%s,%s,%s,%s,%s,%s,%s,%s);',
                (rid,name,theme,competition,title,author,affiliation,number))
        if cur.rowcount != 1:
            return ('EDB',None)
        yield cur.execute('SELECT COUNT(*) FROM "paper" '
                'WHERE "paper"."theme" = %s AND "paper"."competition" = %s;',(theme,competition))
        if cur.rowcount != 1:
            return ('EDB',None);
        pid = str(cur.fetchone()[0])
        filename = theme+'-'+'P-'+('%03d'%int(pid))+'-'+('Y' if int(competition)==1 else 'N')+'-'+name+'.'+f.filename.split('.')[-1]
        yield cur.execute('UPDATE "paper" set filename = %s,pid = %s WHERE "paper"."rid" = %s;',
                (filename,pid,rid))
        if cur.rowcount != 1:
            return('EDB',None)
        path = '../http/paper/'+filename
        _f = open(path,'wb')
        _f.write(f['body']) 
        _f.close()
        return (None,pid)

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


class PaperuploadHandler(RequestHandler):
    @reqenv
    def get(self):
        uid = self.get_secure_cookie('uid')
        if not uid:
            self.redirect('/paper#/third')
            return
        uid = str(int(uid))
        err, abstract = yield from PaperuploadService.inst.get_abstract_info(uid)
        self.render('../http/paperupload_2.html',acct=self.acct, abstract=abstract)
        return

    @reqenv
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
        self.finish(str(aid))
'''
    @reqenv
    def post(self):
        f = self.request.files['paper'][0]
        rid = str(self.get_argument('rid'))
        name = str(self.get_argument('name'))
        theme = str(self.get_argument('theme'))
        competition = str(self.get_argument('competition'))
        title = str(self.get_argument('title'))
        author = str(self.get_argument('author'))
        affiliation = str(self.get_argument('affiliation'))
        number = str(self.get_argument('number'))
        err,pid = yield from PaperuploadService.inst.upload(rid,name,theme,
                competition,title,author,affiliation,number,f)
        if err:
            self.finish(err)
            return
        self.finish(str(pid))
        return
'''
