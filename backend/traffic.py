from req import RequestHandler
from req import reqenv
from req import Service

class TrafficHandler(RequestHandler):
    @reqenv
    def get(self):
        self.render('../http/traffic.html',acct=self.acct)
        return

    @reqenv
    def post(self):
        pass
