from req import reqenv
from req import RequestHandler
from req import Service

class AdminService:
    def __init__(self, db):
        self.db = db
        AdminService.inst = self

class AdminHandler(RequestHandler):
    @reqenv
    def get(self):
        self.render('../http/admin.html', admin=self.admin)
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
