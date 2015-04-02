import tornado.ioloop
import tornado.web 
from news import NewsHandler
from news import NewsService
from manage import ManageHandler
from manage import ManageService
from user import SignupHandler
from user import SigninHandler
from user import UserService
from user import LogoutHandler
from register import RegisterService
from register import RegisterHandler
from register import IndivisualregHandler
from intro import IntroHandler
from agenda import AgendaHandler
from paper import PaperHandler
from english import EnglishHandler
from car import CarHandler
from sponsor import SponsorHandler
from company import CompanyHandler
from venue import VenueHandler
from traffic import TrafficHandler
from paperupload import PaperuploadHandler
from paperupload import PaperuploadService
from mail import MailHandler
from req import Service
from req import reqenv
from req import RequestHandler
from paper import PaperService

import pg

class IndexHandler(RequestHandler):
    @reqenv
    def get(self):
        self.render('../http/index_1.html',page = 'index',acct = self.acct)
        return 

class test(RequestHandler):
    @reqenv
    def get(self):
        self.render('../http/test.html',acct=self.acct)
        return
    @reqenv
    def post(self):
        print(self.request.files)
        print(str(self.get_argument('in')))
        return

if __name__ == '__main__':
    db = pg.AsyncPG('web','admin','adminpassword',dbtz='+8')
    app = tornado.web.Application([
        ('/',IndexHandler),
        ('/test',test),
        ('/news',NewsHandler),
        ('/manage/(.+)',ManageHandler),
        ('/signup',SignupHandler),
        ('/signin',SigninHandler),
        ('/register',RegisterHandler),
        ('/logout',LogoutHandler),
        ('/intro',IntroHandler),
        ('/agenda',AgendaHandler),
        ('/paper',PaperHandler),
        ('/english',EnglishHandler),
        ('/car',CarHandler),
        ('/sponsor',SponsorHandler),
        ('/company',CompanyHandler),
        ('/venue',VenueHandler),
        ('/venue/(.*)',VenueHandler),
        ('/traffic',TrafficHandler),
        ('/indivisualreg',IndivisualregHandler),
        ('/paperupload',PaperuploadHandler),
        ('/(.*)',tornado.web.StaticFileHandler,{'path':'../http/'})
        ],cookie_secret = 'cookie',autoescape = 'xhtml_escape')
    app.listen(88)
    Service.News = NewsService(db)
    Service.Manage = ManageService(db)
    Service.User = UserService(db)
    Service.Register = RegisterService(db)
    Service.Paperupload = PaperuploadService(db)
    Service.Paper = PaperService(db)
    tornado.ioloop.IOLoop.instance().start()
