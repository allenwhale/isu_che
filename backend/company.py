from req import RequestHandler
from req import reqenv
from req import Service

class CompanyHandler(RequestHandler):
    @reqenv
    def get(self):
        self.render('../http/company.html',acct=self.acct)
        return

    @reqenv
    def post(self):
        pass
