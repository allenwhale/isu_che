from req import RequestHandler
from req import reqenv
from req import Service

class SponsorHandler(RequestHandler):
    @reqenv
    def get(self):
        self.render('../http/sponsor.html',acct=self.acct)
        return

    @reqenv
    def post(self):
        pass
