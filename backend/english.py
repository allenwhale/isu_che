from req import RequestHandler
from req import reqenv
from req import Service

class EnglishHandler(RequestHandler):
    @reqenv
    def get(self):
        self.render('../http/english.html',acct=self.acct)
        return

    @reqenv
    def post(self):
        pass
