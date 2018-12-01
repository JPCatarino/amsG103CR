import cherrypy
from jinja2 import Environment, PackageLoader, select_autoescape
import os
from datetime import datetime
import psycopg2
from psycopg2 import Error


class WebApp(object):

    def __init__(self):
        self.env = Environment(
            loader=PackageLoader('webapp', 'HTML'),
            autoescape=select_autoescape(['html', 'xml'])
        )

        self.connect_string = "dbname='ams103' user='ams103' password='pic103ams' host='deti-aulas.ua.pt' port=5432"
        self.users = ["Atleta", "Admin", "Organizador", "Patrocinador"]


    ########################################################################################################################
    #   Utilities

    def set_user(self, username=None):
        if username == None:
            cherrypy.session['user'] = {'is_authenticated': False, 'username': ''}
        else:
            cherrypy.session['user'] = {'is_authenticated': True, 'username': username}


    def get_user(self):
        if not 'user' in cherrypy.session:
            self.set_user()
        return cherrypy.session['user']


    def render(self, tpg, tps):
        template = self.env.get_template(tpg)
        return template.render(tps)


    def db_connection(conString):
        try:
            conn = psycopg2.connect(conString)
            return conn
        except Error as e:
            print(e)
        return None


    def do_authenticationDB(self, usr, pwd):
        user = self.get_user()
        db_con = WebApp.db_connection(self.connect_string)
        sql = "SELECT pwd,typeu FROM utilizador WHERE username == '{}';".format(usr)
        curr = db_con.cursor()
        curr.execute(sql)


        if curr != None:
            if curr[0] == pwd:
                self.set_user(usr)
            db_con.close()

            return curr[1]


    def do_regDB(self, usr, pwd, typeU):
        if typeU not in self.users:
            return None


        db_con = WebApp.db_connection(self.connect_string)
        sql = "INSERT INTO utilizador(username,password,typeU) VALUES ({},{},{});".format(usr, pwd, typeU)
        curr = db_con.cursor()
        curr.execute(sql)
        db_con.commit()
        if typeU == "Atleta":
            sql = "INSERT INTO atleta(username) VALUE ({});".format(usr)
        elif typeU == "Organizador":
            sql = "INSERT INTO organizador(username) VALUE ({});".format(usr)
        elif typeU == "Patrocinador":
            sql = "INSERT INTO patrocinador(username) VALUE ({});".format(usr)

        curr.execute(sql)
        db_con.commit()
        curr.close()
        db_con.close()


    ########################################################################################################################
    #   Controllers


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
    def create(self, usr=None, pwd=None):
        if usr == None:
            tparams = {
                'title': 'Create',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year,
            }
            return self.render('create.html', tparams)
        else:

            if not self.get_user()['is_authenticated']:
                tparams = {
                    'title': 'Create',
                    'errors': True,
                    'user': self.get_user(),
                    'year': datetime.now().year,
                }
                return self.render('create.html', tparams)
            else:
                self.do_regDB(usr, pwd)
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
        '/HTML/assets': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './HTML/assets'
        }
    }
    cherrypy.quickstart(WebApp(), '/', conf)
