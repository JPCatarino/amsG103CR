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
    def get_userid(self):

        db_con = self.db_connection()
        cur = db_con.cursor()
        if self.get_user()['type'] == 'Atleta':
            sql1 = "select a_id from atleta where username = '" + self.get_user()['username'] + "'"
            cur.execute(sql1)
        elif self.get_user()['type'] == 'Organizador':
            sql1 = "select o_id from organizador where username = '" + self.get_user()['username'] + "'"
            cur.execute(sql1)
        elif self.get_user()['type'] == 'Patrocinador':
            sql1 = "select p_id from patrocinador where username = '" + self.get_user()['username'] + "'"
            cur.execute(sql1)
        idu = cur.fetchone()

        cur.close()
        db_con.close()
        return idu[0]

    def criarevento(self,nomeev,data,local,hora,nmax,insc):
        try:
            if (nomeev != '' or nomeev is not None) and (data != '' or data is not None) and (local != '' or local is not None)\
                    and (hora != '' or hora is not None) and (nmax != '' or nmax is not None) and (insc != '' or insc is not None):
                id_o = self.get_userid()
                db_con = self.db_connection()
                cur = db_con.cursor()
                sql = "INSERT INTO evento(nomeevent,datae,hora,locale,nmaxp,valorinsc,estado) VALUES ('" + nomeev + "','" + data + "','" + hora + "','" + local + "',"+str(nmax)+","+ str(insc)+ ",'"+'pendente'+"')"
                cur.execute(sql)
                db_con.commit()
                sql2 = "select id_evento from evento where nomeevent = '" + nomeev+ "'"
                cur.execute(sql2)
                id_e = cur.fetchone()
                sql3 = "INSERT INTO organizadorevento(o_id,id_evento) VALUES (" + str(id_o) + "," + str(id_e[0]) + ")"
                cur.execute(sql3)
                db_con.commit()
        except psycopg2.Error as e:
            return e
        cur.close()
        db_con.close()
        return "no error"

    def get_eventos(self,usr):

        if self.get_user()['type'] == 'Atleta':
            id_a = self.get_userid()
            db_con = self.db_connection()
            cur = db_con.cursor()
            sql2 = "select id_evento from atletaevento where a_id = " + str(id_a) + " and estadopagamento='Pago'"
            cur.execute(sql2)
            id_event = cur.fetchone()

            for e in id_event:
                sql3 = "select * from evento where id_evento = " + str(e[0]) + " and estado='Disponivel'"
                cur.execute(sql3)
                data = cur.fetchone()
                cherrypy.session['event'] +=[data]
        elif self.get_user()['type'] == 'Organizador':
            id_o = self.get_userid()
            db_con = self.db_connection()
            cur = db_con.cursor()
            sql2 = "select id_evento from organizadorevento where o_id = " + str(id_o)
            cur.execute(sql2)
            id_event = cur.fetchone()
            for e in id_event:
                sql3 = "select * from evento where id_evento = " + str(e[0])  + " and estado='Disponivel' or estado = 'Pendente'"
                cur.execute(sql3)
                data = cur.fetchone()
                cherrypy.session['event'] += [data]
        elif self.get_user()['type'] == 'Patrocinador':
            id_p = self.get_userid()
            db_con = self.db_connection()
            cur = db_con.cursor()
            sql2 = "select id_evento,valorpatrocinado,estadopedido from patrocinadorevento where p_id =" + id_p
            cur.execute(sql2)
            id_event = cur.fetchone()
            for e in id_event:
                sql3 = "select * from evento where id_evento = " + str(e[0]) + " and estado='Disponivel'"
                cur.execute(sql3)
                data = cur.fetchone()
                cherrypy.session['event'] += [data]

        cur.close()
        db_con.close()
        return cherrypy.session['event']

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

    def changepassword(self, usr, newpwd,password):
        db_json = json.load(open(WebApp.dbjson))
        users = db_json['users']
        index = 0
        for u in users:
            if u['username'] == usr :
                if(db_json['users'][index]['password']==password):
                    db_json['users'][index]['password'] = newpwd
                    jsonFile = open(WebApp.dbjson, "w+")
                    jsonFile.write(json.dumps(db_json, indent=4))
                    jsonFile.close()
                    return True
                else:
                    return False
            index+=1
    
    def changeusername(self, usr, newusr,password):
        db_json = json.load(open(WebApp.dbjson))
        users = db_json['users']
        index = 0
        for u in users:
            if u['username'] == usr :
                if(db_json['users'][index]['password']==password):
                    db_json['users'][index]['admin'] = newusr
                    jsonFile = open(WebApp.dbjson, "w+")
                    jsonFile.write(json.dumps(db_json, indent=4))
                    jsonFile.close()
                    return True
                else:
                    return False
            index+=1
        
    def changeemail(self, usr, newemail,password):
        db_json = json.load(open(WebApp.dbjson))
        users = db_json['users']
        index = 0
        for u in users:
            if u['username'] == usr :
                if(db_json['users'][index]['password']==password):
                    db_json['users'][index]['email'] = newemail
                    jsonFile = open(WebApp.dbjson, "w+")
                    jsonFile.write(json.dumps(db_json, indent=4))
                    jsonFile.close()
                    return True
                else:
                    return False
            index+=1

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
    def noticias(self):
        tparams = {
            'user': self.get_user(),
            'year': datetime.now().year,
        }
        return self.render('noticias.html', tparams)

    @cherrypy.expose
    def criarevento(self,nomeev=None,data=None,local=None,hora=None,nmax=None,insc=None):

        if nomeev == '' or nomeev is None:
            tparams = {
                'title': 'CriarEvento',
                'user': self.get_user(),
                'year': datetime.now().year,
                'errors': False,
            }
            return self.render('criarevento.html', tparams)
        else:
            if self.get_user()['is_authenticated']:
               error = self.criarevent(nomeev,data,local,hora,nmax,insc)
               if error == "no error":
                   raise cherrypy.HTTPRedirect("/Organizador")
               else:
                   tparams = {
                       'title': 'CriarEvento',
                       'user': self.get_user(),
                       'year': datetime.now().year,
                       'errors': True,
                   }
                   return self.render('criarevento.html', tparams)

    
    @cherrypy.expose
    def meventosa(self):
        tparams = {
            'user': self.get_user(),
            'year': datetime.now().year,
        }

        return self.render('meventosa.html', tparams)
        
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
