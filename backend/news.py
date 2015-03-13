from req import Service
from req import RequestHandler
from req import reqenv
class NewsService:
    def __init__(self,db):
        self.db = db
        NewsService.inst = self

    def get_title_list(self):
        cur = yield self.db.cursor()
        try:
            yield cur.execute(('SELECT "news"."id", "news"."title", '
                '"news"."timestamp","news"."top" FROM '
                '"news" ORDER BY "news"."top" DESC,"news"."timestamp" DESC;'),())
        except:
            return ('EDB1',None)
        title_list = []
        for id,title,time,top in cur:
            title_list.append({"id":id,'title':title,
                'time':time.strftime('%Y-%m-%d'),'top':top})
        return (None,title_list)

    def get_news_by_id(self,_id):
        cur = yield self.db.cursor()
        try:
            yield cur.execute(('SELECT "news"."id", '
                '"news"."title", "news"."content", '
                '"news"."attachment_name", "news"."attachment_link", '
                '"news"."timestamp","news"."top" FROM "news" '
                'WHERE "news"."id" = %s;'),(_id,))
        except:
            return ('EDB1',None)
        if cur.rowcount != 1:
            return ('EDB2',None)
        meta = cur.fetchone()
        meta = {'id':meta[0],
                'title':meta[1],
                'content':meta[2],
                'attachment':zip(meta[3],meta[4]),
                'time':meta[5].strftime('%Y-%m-%d'),
                'top':meta[6]}
        return (None,meta)

    def add_news(self,title,top,content,attachment_name,attachment_link):
        cur = yield self.db.cursor()
        yield cur.execute('INSERT INTO "news" (title,top,content,attachment_name,attachment_link)'
                'VALUES(%s,%s,%s,\'{'+attachment_name+'}\',\'{'+attachment_link+'}\') RETURNING "news"."id";',
                (title,top,content))
        if cur.rowcount != 1:
            return('EDB',None)
        nid = str(cur.fetchone()[0])
        return (None,nid)

    def del_news(self,nid):
        cur = yield self.db.cursor()
        yield cur.execute('DELETE FROM "news" WHERE "news"."id" = %s;',(nid,))
        if cur.rowcount != 1:
            return('Enoexist',None)
        return(None,nid)
        
class NewsHandler(RequestHandler):
    @reqenv
    def get(self):
        try:
            page = int(self.get_argument('page'))
        except:
            page = None
        if page == None:
            title_list = []
            err,title_list = yield from NewsService.inst.get_title_list()
            if err:
                self.finish(err)
                return
            self.render('../http/news.html',now = 'news',title_list = title_list,acct = self.acct)
            return
        else:
            err,meta = yield from NewsService.inst.get_news_by_id(page);
            if err:
                print(err)
                return
            self.render('../http/news_page.html',now = 'news',
                    meta = meta,acct = self.acct)
            return
