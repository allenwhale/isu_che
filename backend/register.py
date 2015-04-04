from req import RequestHandler
from req import reqenv
from req import Service
from mail import MailHandler

class RegisterService():
    def __init__(self,db):
        self.db = db
        RegisterService.inst = self

    def register(self,name,title,affiliation,department,
            address,postcode,email,phone,fax,cellphone,
            member,package,banquet,total,food,food_date1,
            food_date2,agenda,paper,transnum,transmulti,invoice,vat):
        cur = yield self.db.cursor()
        yield cur.execute('SELECT 1 FROM "register" WHERE "register"."name" = %s;',(name,))
        if cur.rowcount != 0:
            return ('Eexistname',None)
        yield cur.execute('SELECT 1 FROM "register" WHERE "register"."email" = %s;',(email,))
        if cur.rowcount != 0:
            return ('Eexistemail',None)
        yield cur.execute('INSERT INTO "register" ( "name","title","affiliation",'
                '"department","address","postcode","email","phone","fax","cellphone",'
                '"member","package","banquet","total","food","food_date1","food_date2",'
                '"agenda","paper","transnum","transmulti","invoice","vat") '
                'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) '
                'RETURNING "register"."rid";',(name,title,affiliation,department,
                    address,postcode,email,phone,fax,cellphone,member,package,banquet,
                    total,food,food_date1,food_date2,agenda,paper,transnum,transmulti,invoice,vat))
        if cur.rowcount != 1:
            return ('EDB',None)
        return (None,cur.fetchone()[0])

class RegisterHandler(RequestHandler):
    @reqenv
    def get(self):
        self.render('../http/register.html',page='register',acct=self.acct)
        return
    @reqenv
    def post(self):
        pass

class IndivisualregHandler(RequestHandler):
    @reqenv
    def get(self):
        self.render('../http/indivisualreg.html',acct=self.acct)
        return

    @reqenv
    def post(self):
        name = str(self.get_argument('name'))
        title = str(self.get_argument('title'))
        affiliation = str(self.get_argument('affiliation'))
        department = str(self.get_argument('department'))
        address = str(self.get_argument('address'))
        postcode = str(self.get_argument('postcode'))
        email = str(self.get_argument('email'))
        phone = str(self.get_argument('email'))
        fax = str(self.get_argument('fax'))
        cellphone = str(self.get_argument('cellphone'))
        member = str(self.get_argument('member'))
        package = str(self.get_argument('package'))
        banquet = str(self.get_argument('banquet'))
        total = str(self.get_argument('total'))
        food = str(self.get_argument('food'))
        food_date1 = str(self.get_argument('food_date1'))
        food_date2 = str(self.get_argument('food_date2'))
        agenda = str(self.get_argument('agenda'))
        paper = str(self.get_argument('paper'))
        transnum = str(self.get_argument('transnum'))
        transmulti = str(self.get_argument('transmulti'))
        invoice = str(self.get_argument('invoice'))
        vat = str(self.get_argument('vat'))
        err,rid = yield from RegisterService.inst.register(
                name,title,affiliation,department,address,postcode,
                email,phone,fax,cellphone,member,package,banquet,total,
                food,food_date1,food_date2,agenda,paper,transnum,transmulti,invoice,vat)
        if err:
            self.finish(err)
            return
        m = MailHandler('../http/register_mail.html')
        m.send(to=email, subject='台灣化學工程學會62th年會報名確認', rid='%04d'%rid)
        self.finish('%04d'%int(rid))
        return
