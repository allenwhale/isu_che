from req import Service
from req import RequestHandler
from req import reqenv

class ManageService:
    def __init__(self,db):
        self.db = db
        ManageService.inst = self
    
class ManageHandler(RequestHandler):
    @reqenv
    def get(self,page = 'sign'):
        if page == '':
            page = 'sign'
        print(page)
        if page == 'sign':
            self.render('../http/manage-sign.html',now = 'manage',acct = self.acct)
            return
        elif page == 'news':
            title_list = []
            err,title_list = yield from Service.News.get_title_list()
            if err:
                self.finish(err)
                return
            self.render('../http/manage-news.html',now = 'manage',acct = self.acct,title_list = title_list)
            return
        return
    @reqenv
    def post(self,page):
        if page == 'news':
            _type = str(self.get_argument('type'))
            if _type == 'add':
                title = str(self.get_argument('title'))
                top = str(self.get_argument('top'))
                content = str(self.get_argument('content'))
                attach_name = str(self.get_argument('attach_name'))
                attach_link = str(self.get_argument('attach_link'))
                if len(attach_name.split(',')) != len(attach_link.split(',')):
                    mn = min(len(attach_name.split(',')),len(attach_link.split(',')))
                    attach_name = str(attach_name.split(',')[:mn])[1:-1]
                    attach_link = str(attach_link.split(',')[:mn])[1:-1]
                err,nid = yield from Service.News.add_news(title,top,content,attach_name,attach_link)
                if err:
                    self.finish(err)
                    return
                self.finish(str(nid))
                return
            elif _type == 'del':
                nid = str(self.get_argument('nid'))
                err,rnid = yield from Service.News.del_news(nid)
                if err:
                    self.finish(err)
                    return
                self.finish(str(rnid))
                return
            return

        return
