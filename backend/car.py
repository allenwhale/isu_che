from req import RequestHandler
from req import reqenv
from req import Service

class CarHandler(RequestHandler):
    @reqenv
    def get(self):
        self.render('../http/car.html',acct=self.acct)
        return

    @reqenv
    def post(self):
        pass
