from req import RequestHandler
from req import reqenv
from req import Service

class AgendaHandler(RequestHandler):
    @reqenv
    def get(self):
        self.render('../http/agenda.html',acct=self.acct)
        return

    @reqenv
    def post(self):
        pass
