import cherrypy
import os
from datetime import datetime
import psycopg2


baseDir = os.path.dirname(os.path.abspath(__file__))
# Dict with the this app's configuration:
config = {
    "/":       {"tools.staticdir.root": baseDir},
    "/HTML": {"tools.staticdir.on": True, "tools.staticdir.dir": os.path.join(baseDir, "HTML")},

}


class Root(object):
    def __init__(self):
        self.api = api()

    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect("/HTML/CityRunning.html")

class api(object):
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
        conn = psycopg2.connect(conString)
        return conn


    def do_authenticationDB(self, usr, pwd):
        user = self.get_user()
        db_con = Root.db_connection(self.connect_string)
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

        db_con = Root.db_connection(self.connect_string)
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



if __name__ == '__main__':
    cherrypy.quickstart(Root(), "/", config)