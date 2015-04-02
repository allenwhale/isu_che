from req import RequestHandler
from req import reqenv
from req import Service

class VenueHandler(RequestHandler):
    @reqenv
    def get(self, page=None):
        if page == 'royal':
            self.render('../http/venue-royal.html',acct=self.acct)
            return
        elif page == 'skylard':
            self.render('../http/venue-skylard.html',acct=self.acct)
            return
        elif page == 'isu':
            self.render('../http/venue-isu.html',acct=self.acct)
            return
        else:
            self.render('../http/venue.html',acct=self.acct)
            return
        return

    @reqenv
    def post(self):
        pass
