import cherrypy
from jinja2 import Environment, PackageLoader, select_autoescape
import os
from datetime import datetime
import psycopg2
from psycopg2 import Error
import json


class WebApp(object):
    def __init__(self):
        self.env = Environment(
                loader=PackageLoader('webapp', 'templates'),
                autoescape=select_autoescape(['html', 'xml'])
                )


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
        sql = "select pwd from utilizador where username = '" + usr+ "'"
        cur = db_con.cursor()
        cur.execute(sql)
        try:
            row = cur.fetchone()
            if row is not None:
                if row[0] == pwd:
                    self.set_user(usr)
        except psycopg2.Error as e:
            print(e)

        cur.close()
        db_con.close()



    def do_regDB(self,usr,pwd,mail,typeu):
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
    def signup(self,usr=None,pwd=None,mail=None,typeu=None):
        if usr == None:
            tparams = {
                'title': 'SignUp',
                'errors': False,
                'user': self.get_user(),
                'year': datetime.now().year,
            }
            return self.render('signup.html', tparams)
        else:
            self.do_regDB(usr,pwd,mail,typeu)
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
