from req import RequestHandler
from req import reqenv
from req import Service

class VenueHandler(RequestHandler):
    @reqenv
    def get(self):
        self.render('../http/venue.html',acct=self.acct)
        return

    @reqenv
    def post(self):
        pass
