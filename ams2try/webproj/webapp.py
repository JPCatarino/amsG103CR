import cherrypy
from jinja2 import Environment, PackageLoader, select_autoescape
import os
from datetime import datetime
import psycopg2



class WebApp(object):
    def __init__(self):
        self.env = Environment(
                loader=PackageLoader('webapp', 'templates'),
                autoescape=select_autoescape(['html', 'xml'])
                )


########################################################################################################################
#   Utilities
    def get_eventos(self,usr):
        data=[]

        db_con = self.db_connection()
        cur = db_con.cursor()
        if self.get_user()['type'] == 'Atleta':
            sql1 = "select a_id from atleta where username = '" + usr+ "'"
            cur.execute(sql1)
            id_a=cur.fetchone()
            sql2 = "select id_evento from atletaevento where a_id = '" + id_a+ "'" + "and estadopagamento='Pago'"
            cur.execute(sql2)
            id_event = cur.fetchone()
            for e in id_event:
                sql3 = "select * from evento where id_evento = '" + e + "'" + "and estado='Disponivel'"
                cur.execute(sql3)
                data+=[cur.fetchone]
        elif self.get_user()['type'] == 'Organizador':
            sql1 = "select o_id from organizador where username = '" + usr + "'"
            cur.execute(sql1)
            id_a = cur.fetchone()
            sql2 = "select id_evento from organizadorevento where a_id = '" + id_a + "'"
            cur.execute(sql2)
            id_event = cur.fetchone()
            for e in id_event:
                sql3 = "select * from evento where id_evento = '" + e + "'" + "and estado='Disponivel' or estado = 'Pendente'"
                cur.execute(sql3)
                data += [cur.fetchone]
        elif self.get_user()['type'] == 'Patrocinador':
            sql1 = "select p_id from patrocinador where username = '" + usr + "'"
            cur.execute(sql1)
            id_a = cur.fetchone()
            sql2 = "select id_evento,valorpatrocinado,estadopedido from patrocinadorevento where p_id = '" + id_a + "'"
            cur.execute(sql2)
            id_event = cur.fetchone()
            for e in id_event:
                sql3 = "select * from evento where id_evento = '" + e[0] + "'" + "and estado='Disponivel'"
                cur.execute(sql3)
                data += [cur.fetchone]

        cur.close()
        db_con.close()
    def set_user(self, username=None,type=None):
        if username == None or username == '':
            cherrypy.session['user'] = {'is_authenticated': False, 'username': '', 'type':'' }
        else:
            cherrypy.session['user'] = {'is_authenticated': True, 'username': username , 'type': type}


    def get_user(self):
        if not 'user' in cherrypy.session:
            self.set_user()
        return cherrypy.session['user']


    def render(self, tpg, tps):
        template = self.env.get_template(tpg)
        return template.render(tps)


    def db_connection(self):
        try:
            conn = psycopg2.connect(host='deti-aulas.ua.pt',database='ams103', user='ams103', password='pic103ams')
            return conn
        except psycopg2.Error as e:
            print(e)
        return None


    def do_authenticationDB(self, usr, pwd):
        user = self.get_user()
        db_con = self.db_connection()
        sql = "select pwd,typeu from utilizador where username = '" + usr+ "'"
        cur = db_con.cursor()
        cur.execute(sql)
        try:
            row = cur.fetchone()
            if row is not None:
                if row[0] == pwd:
                    self.set_user(usr,row[1])
        except psycopg2.Error as e:
            print(e)

        cur.close()
        db_con.close()



    def do_regDB(self,usr,pwd,mail,typeu):
        if usr is not None or usr != '' and pwd is not None or pwd != '' and mail is not None or mail != '' and \
                typeu is not None or typeu != '':
            db_con = self.db_connection()
            sql = "INSERT INTO utilizador(username,pwd,typeu,mail) VALUES ('"+usr +"','" + pwd+"','"+typeu+"','"+mail+"')"
            cur = db_con.cursor()
            cur.execute(sql)
            db_con.commit()
            if typeu == 'Atleta':
                sql = "INSERT INTO atleta(username) VALUES ('"+usr +"')"
            elif typeu == 'Organizador':
                sql = "INSERT INTO organizador(username) VALUES ('"+usr +"')"
            elif typeu == 'Patrocinador':
                sql = "INSERT INTO patrocinador(username) VALUES ('"+usr +"')"
            cur.execute(sql)
            db_con.commit()

            cur.close()
            db_con.close()

    ########################################################################################################################
#   Controllers

    @cherrypy.expose
    def index(self):
        tparams = {
            'user': self.get_user(),
            'year': datetime.now().year,
        }
        return self.render('index.html', tparams)

    @cherrypy.expose
    def meventosa(self):
        tparams = {
            'user': self.get_user(),
            'year': datetime.now().year,
        }

        return self.render('meventosa.html', tparams)


    @cherrypy.expose
    def about(self):
        tparams = {
            'title': 'About',
            'message': 'Your application description page.',
            'user': self.get_user(),
            'year': datetime.now().year,
        }
        return self.render('about.html', tparams)


    @cherrypy.expose
    def contact(self):
        tparams = {
            'title': 'Contact',
            'message': 'Your contact page.',
            'user': self.get_user(),
            'year': datetime.now().year,
        }
        return self.render('contact.html', tparams)


    @cherrypy.expose
    def login(self, username=None, password=None):
        if username == None:
            tparams = {
                'title': 'Login',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year,
            }
            return self.render('login.html', tparams)
        else:
            self.do_authenticationDB(username, password)
            if not self.get_user()['is_authenticated']:
                tparams = {
                    'title': 'Login',
                    'errors': True,
                    'user': self.get_user(),
                    'year': datetime.now().year,
                }
                return self.render('login.html', tparams)
            else:
                raise cherrypy.HTTPRedirect("/")
    @cherrypy.expose
    def logout(self):
        self.set_user()
        raise cherrypy.HTTPRedirect("/")


    @cherrypy.expose
    def signup(self, usr=None, pwd=None, mail=None, typeu=None):
        if usr is None or usr == '':
            tparams = {
                'title': 'SignUp',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year,
            }
            return self.render('signup.html', tparams)
        else:
            self.do_regDB(usr, pwd, mail, typeu)
            raise cherrypy.HTTPRedirect("/")




    @cherrypy.expose
    def shut(self):
        cherrypy.engine.exit()


if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './static'
        }
    }
    cherrypy.quickstart(WebApp(), '/', conf)
