from req import reqenv
from req import RequestHandler
from req import Service
import datetime
import subprocess
from shutil import move
from shutil import copy2
from os import mkdir
from os import remove

class AdminService:
    def __init__(self, db):
        self.db = db
        AdminService.inst = self

    def get_account_info(self, admin):
        if not admin:
            return ('Eaccess', None)
        cur = yield self.db.cursor()
        yield cur.execute('SELECT "rid" FROM "register";')
        user_list = [ t[0] for t in cur]
        meta = []
        for user in user_list:
            err, sub = yield from Service.User.get_acct_meta(user)
            if not err:
                meta.append(sub)
        return (None, meta)

    def gen_csv_info(self,admin):
        err, meta = yield from self.get_account_info(admin)
        if err:
            return (err, None)
        args = ['rid','invoice','affiliation','transnum','vat','phone','title','food','name','total','member','department','package','email','address','created']
        paper = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'TKJ1:', 'TKJ2:']
        filename = '../http/'+str(datetime.datetime.now().strftime('%Y-%m-%d'))+'info.csv'
        f = open(filename, 'wb')
        for t in args:
            if t == 'rid':
                f.write('uid,'.encode('big5'))
            else:
                f.write((t+',').encode('big5'))
        for p in paper:
            f.write((p+',').encode('big5'))
        f.write('\n'.encode('big5'))
        for m in meta:
            for a in args:
                if a == 'food':
                    ff = ['素','葷','XXX']
                    f.write((ff[int(m[a])]+',').encode('big5'))
                elif a == 'rid':
                    f.write(('="%04d",'%(int(m[a]))).encode('big5'))
                elif a == 'email':
                    f.write(('"%s",'%(m[a])).encode('big5'))
                elif a == 'phone':
                    f.write(('="%s",'%(m[a])).encode('big5'))
                elif a == 'vat':
                    f.write(('="%s",'%m[a]).encode('big5'))
                else:
                    f.write((str(m[a])+',').encode('big5'))

            for p in paper:
                if p in m['paper']:
                    f.write('YES,'.encode('big5'))
                else:
                    f.write('NO,'.encode('big5'))
            f.write('\n'.encode('big5'))
        f.close()
        return (None, filename)
    
    def get_abstract_info(self, admin):
        if not admin:
            return ('Eaccess', None)
        cur = yield self.db.cursor()
        yield cur.execute('SELECT "rid" FROM "register" ORDER BY "rid";')
        user_list = [ c[0] for c in cur ]
        meta = []
        for user in user_list:
            yield cur.execute('SELECT "topic", "title", "op", "affiliation", "author", "number", "aid", "modified" FROM "abstract" WHERE "uid" = %s;', (user, ))
            if cur.rowcount == 1:
                sub = cur.fetchone()
                meta.append({'uid':user,
                    'topic':sub[0] ,
                    'title':sub[1],
                    'op':sub[2],
                    'affiliation':sub[3],
                    'author':sub[4],
                    'number':sub[5],
                    'aid': sub[6],
                    'modified': sub[7]
                    })
        return (None, meta)

    def gen_csv_abstract(self, admin):
        if not admin:
            return ('Eaccess', None)
        err, meta = yield from self.get_abstract_info(admin)
        if err:
            return(err, None)
        filename = '../http/'+str(datetime.datetime.now().strftime('%Y-%m-%d'))+'abs.csv'
        args = ['uid','topic', 'title', 'op', 'affiliation', 'number', 'author', 'modified']
        f = open(filename, 'wb')
        for a in args:
            if a == 'op':
                f.write('presentationi,'.encode('big5'))
            else:
                f.write((a+',').encode('big5'))
        f.write('\n'.encode('big5'))
        for m in meta:
            for a in args:
                if a == 'uid':
                    f.write(('="%04d",'%m[a]).encode('big5'))
                else:
                    f.write((str(m[a])+',').encode('big5'))
            f.write('\n'.encode('big5'))
        f.close()
        return (None, filename)
    
    def pack_abstract(self, admin):
        if not admin:
            return ('Eaccess', None)
        err, meta = yield from self.get_abstract_info(admin)
        if err:
            return (err, None)
        topic_class = ['A.', 'B.', 'C.', 'D.', 'E.', 'F.', 'G.', 'H.', 'I.', 'TKJ1:', 'TKJ2:']
        cnt = {}
        for t in topic_class:
            cnt[t] = {'o':1,'p':1, 'i':1}

        dirname = str(datetime.datetime.now().strftime('%Y-%m-%d'))
        subprocess.call(['rm','-rf','../http/'+dirname])
        mkdir('../http/'+dirname)
        for m in meta:
            uid = m['uid']
            aid = m['aid']
            for t in topic_class:
                if t in m['topic']:
                    clas = t
                    ID = cnt[t][m['op']]
                    cnt[t][m['op']] += 1
            srcpath = '../http/paper/'+str(uid)+'/'
            dstpath = '../http/'+dirname+'/'
            sub = subprocess.Popen('find '+srcpath+' | grep abs', shell=True, stdout=subprocess.PIPE)
            sub = sub.communicate()[0].decode()
            if sub[-1] == '\n':
                sub = sub[:-1]
            print(sub)
            copy2(sub,dstpath+clas[:-1]+m['op'].upper()+'-%03d-'%ID+'%04d-Abs'%m['uid']+'.'+sub.split('.')[-1])
            sub = subprocess.Popen('find '+srcpath+' | grep cop', shell=True, stdout=subprocess.PIPE)
            sub = sub.communicate()[0].decode()
            if sub[-1] == '\n':
                sub = sub[:-1]
            print(sub)
            copy2(sub,dstpath+clas[:-1]+m['op'].upper()+'-%03d-'%ID+'%04d-Cop'%m['uid']+'.'+sub.split('.')[-1]) 
            try:
                remove('../http/'+dirname+'.zip')
            except:
                pass
            subprocess.call('zip -jr ../http/'+dirname+'.zip ../http/'+dirname+'/',shell=True)
        return (None, dirname)
            


class AdminHandler(RequestHandler):
    @reqenv
    def get(self):
        err, filename = yield from AdminService.inst.gen_csv_info(self.admin)
        err, meta = yield from AdminService.inst.get_abstract_info(self.admin)
        err, filename = yield from AdminService.inst.gen_csv_abstract(self.admin)
        err, dirname = yield from AdminService.inst.pack_abstract(self.admin)
        self.render('../http/admin.html', admin=self.admin,csv=str(datetime.datetime.now().strftime('%Y-%m-%d')+'info.csv'),_abs=str(datetime.datetime.now().strftime('%Y-%m-%d')+'abs.csv'),_zip=str(dirname)+'.zip')

        return

    @reqenv
    def post(self):
        req = self.get_argument('req', None)
        print(req)
        if req == 'login':
            pwd = self.get_argument('pwd', None)
            if pwd == 'admin':
                self.set_secure_cookie('admin','1')
                self.finish('S')
                return
            self.finish('密碼錯誤')
        elif req == 'logout':
            self.clear_cookie('admin')
            self.finish('S')
        pass
