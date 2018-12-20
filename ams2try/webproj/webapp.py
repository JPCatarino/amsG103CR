import cherrypy
from jinja2 import Environment, PackageLoader, select_autoescape
import os
from datetime import datetime
import psycopg2

class Eventpast(object):
    def __init__(self, id, nome, tempo):
        self.id = id
        self.nome = nome
        self.tempo = tempo


class Event(object):
    def __init__(self,id,nome,data,hora,local,nmaxp,valor,organizador=None,estado=None,patrocinado=None):
        self.id = id
        self.nome = nome
        self.data = data
        self.hora = hora
        self.local = local
        self.nmaxp = nmaxp
        self.valor = valor
        if organizador != None:
            self.organizador = organizador
        if estado != None:
            self.estado = estado
        if patrocinado!= None:
            self.patrocinado = patrocinado



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

    def criarevent(self, nomeev, data, local, hora, nmax, insc):
        try:
            if (nomeev != '' or nomeev is not None) and (data != '' or data is not None) and (
                    local != '' or local is not None) \
                    and (hora != '' or hora is not None) and (nmax != '' or nmax is not None) and (
                    insc != '' or insc is not None):
                id_o = self.get_userid()
                db_con = self.db_connection()
                cur = db_con.cursor()
                sql = "INSERT INTO evento(nomeevent,datae,hora,locale,nmaxp,valorinsc,estado) VALUES ('" + nomeev + "','" + data + "','" + hora + "','" + local + "'," + str(
                    nmax) + "," + str(insc) + ",'" + 'pendente' + "')"
                cur.execute(sql)
                db_con.commit()
                sql2 = "select id_evento from evento where nomeevent = '" + nomeev + "'"
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

    def get_eventos(self, usr):
        events =[]
        if self.get_user()['type'] == 'Atleta':
            id_a = self.get_userid()
            db_con = self.db_connection()
            cur = db_con.cursor()
            sql=" select E.id_evento, E.nomeevent, E.datae, E.hora, E.locale, E.nmaxp, E.valorinsc from atletaevento as AE join evento as E ON AE.id_evento= E.id_evento join atleta as A on AE.a_" \
                "id=A.a_id where A.a_id =" + str(id_a) + "and AE.estadopagamento = 'Pago' and E.estado='Disponivel'"

            cur.execute(sql)
            data = cur.fetchone()
            for d in data:
                events.append(Event(d[0],d[1],d[2],d[3],d[4],d[5],d[6],d[7]))
            self.get_user()["events"] = events

        elif self.get_user()['type'] == 'Organizador':
            id_o = self.get_userid()
            db_con = self.db_connection()
            cur = db_con.cursor()
            sql = " select E.id_evento, E.nomeevent, E.datae, E.hora, E.locale, E.nmaxp, E.valorinsc from organizadorevento as OE join evento as E ON OE.id_evento= E.id_evento join organizador as O on OE.o_" \
                  "id=O.o_id where O.o_id =" + str(id_o)

            cur.execute(sql)
            data = cur.fetchone()

            for d in data:
                events.append(Event(d[0],d[1],d[2],d[3],d[4],d[5],d[6],d[7]))
            self.get_user()["events"] = events

        elif self.get_user()['type'] == 'Patrocinador':
            id_p = self.get_userid()
            db_con = self.db_connection()
            cur = db_con.cursor()

            sql = " select E.id_evento, E.nomeevent, E.datae, E.hora, E.locale, E.nmaxp, E.valorinsc,PE.estadopedido,PE.valorpatrocinado from patrocinadorevento as PE join evento as E ON PE.id_evento= E.id_evento join patrocinador as P on PE.p_" \
                  "id=P.p_id where P.p_id =" + str(id_p)

            cur.execute(sql)
            data = cur.fetchone()
            for d in data:
                events.append(Event(d[0],d[7],d[1],d[2],d[3],d[4],d[5],d[6],d[7],d[8]))
            self.get_user()["events"] = events
        cur.close()
        db_con.close()
        return self.get_user()["events"]

    def set_events(self):
        events=[]
        db_con = self.db_connection()
        cur = db_con.cursor()
        sql = "select E.id_event,E.nomeevent,E.datae,E.hora,E.locale,E.nmaxp,E.valorinsc,O.o_id,E.estado from evento AS E JOIN organizadorevento as OE ON E.id_evento = OE.id_evento  JOIN organizador AS O on OE.o_id=O.o_id"
        cur.execute(sql)
        data= cur.fetchone()
        for d in data:
            events.append(Event(d[0],d[1],d[2],d[3],d[4],d[5],d[6],d[7],d[8]))
        cherrypy.session["event"] = events

    def get_historicoatleta(self):
        events = []
        if self.get_user()['type'] == 'Atleta':
            id_a = self.get_userid()
            db_con = self.db_connection()
            cur = db_con.cursor()
            sql = " select E.id_evento, E.nomeevent, ATE.tempo  from atletaevento as AE join evento as E ON AE.id_evento= E.id_evento join atleta as A on AE.a_" \
                  "id=A.a_id join atletasensor as ASE ON E.id_evento= ASE.id_evento and A.a_id = ASE.a_id join atletatempo " \
                  "as ATE on ASE.id_evento = ATE.id_evento and ASE.nsensor = ATE.nsensor  where A.a_id =" + str(id_a) + "and E.estado='Terminado'"

            cur.execute(sql)
            data = cur.fetchone()
            for d in data:
                events.append(Eventpast(d[0],d[1],d[2]))
            self.get_user()["historico"] = events
<<<<<<< HEAD
    
=======
    def set_noticias(self,text):
        user = self.get_user()["username"]
        db_con = self.db_connection()
        cur = db_con.cursor()
        sql = "Insert into noticias(texto,username) values('"+ str(text)+"','" + str(user) + "')"
        cur.execute(sql)
        db_con.commit()
        cur.close()
        db_con.close()

    def get_noticias(self):
        noticias = []
        db_con = self.db_connection()
        cur = db_con.cursor()
        sql = "select texto,username from noticias"
        cur.execute(sql)
        data = cur.fetchone()
        for d in data:
            noticias.append((d[0],d[1]))
        cherrypy.session["noticias"] = noticias
        return cherrypy.session["noticias"]
>>>>>>> b9fdc23656f4177f28588fdf0fad3ee3ebaa986d

    def set_user(self, username=None, type=None):
        if username == None or username == '':
            cherrypy.session['user'] = {'is_authenticated': False, 'username': '', 'type': '', 'events':None, "historico":None}
        else:
            cherrypy.session['user'] = {'is_authenticated': True, 'username': username, 'type': type, 'events': None,
                                        "historico": None}

    def get_user(self):
        if not 'user' in cherrypy.session:
            self.set_user()
        return cherrypy.session['user']

    def render(self, tpg, tps):
        template = self.env.get_template(tpg)
        return template.render(tps)

    def db_connection(self):
        try:
            conn = psycopg2.connect(host='deti-aulas.ua.pt', database='ams103', user='ams103', password='pic103ams')
            return conn
        except psycopg2.Error as e:
            print(e)

    def do_authenticationDB(self, usr, pwd):
        user = self.get_user()
        db_con = self.db_connection()
        sql = "select pwd,typeu from utilizador where username = '" + usr + "'"
        cur = db_con.cursor()
        cur.execute(sql)
        try:
            row = cur.fetchone()
            if row is not None:
                if row[0] == pwd:
                    self.set_user(usr, row[1])
        except psycopg2.Error as e:
            print(e)

        cur.close()
        db_con.close()

    def do_regDB(self, usr, pwd, mail, typeu):
        if usr is not None or usr != '' and pwd is not None or pwd != '' and mail is not None or mail != '' and \
                typeu is not None or typeu != '':
            db_con = self.db_connection()
            sql = "INSERT INTO utilizador(username,pwd,typeu,mail) VALUES ('" + usr + "','" + pwd + "','" + typeu + "','" + mail + "')"
            cur = db_con.cursor()
            cur.execute(sql)
            db_con.commit()
            if typeu == 'Atleta':
                sql = "INSERT INTO atleta(username) VALUES ('" + usr + "')"
            elif typeu == 'Organizador':
                sql = "INSERT INTO organizador(username) VALUES ('" + usr + "')"
            elif typeu == 'Patrocinador':
                sql = "INSERT INTO patrocinador(username) VALUES ('" + usr + "')"
            cur.execute(sql)
            db_con.commit()

            cur.close()
            db_con.close()

    def changepassword(self,newpwd):
        db_con = self.db_connection()
        sql = "UPDATE utilizador SET pwd =" + newpwd + " Where utilizador ="+ self.get_user()["username"]
        cur = db_con.cursor()
        cur.execute(sql)
        db_con.commit()
        cur.close()
        db_con.close()


    def changeemail(self,newemail):
        db_con = self.db_connection()
        sql = "UPDATE utilizador SET mail =" + newemail + " Where utilizador =" + self.get_user()["username"]
        cur = db_con.cursor()
        cur.execute(sql)
        db_con.commit()
        cur.close()
        db_con.close()


    ########################################################################################################################
    # Controller

    @cherrypy.expose
    def index(self):
        tparams = {
            'user': self.get_user(),
            'year': datetime.now().year,
        }
        return self.render('index.html', tparams)

    #######################################################################################################
    ## Estatisticas

    @cherrypy.expose
    def statics(self):
        tparams = {
            'user': self.get_user(),
            'year': datetime.now().year,
        }
        return self.render('statics.html', tparams)

    #######################################################################################################
    ## Mensagens

    @cherrypy.expose
    def mensagem(self):
        tparams = {
            'user': self.get_user(),
            'year': datetime.now().year,
        }
        return self.render('mensagem.html', tparams)

    @cherrypy.expose
    def writesms(self):
        tparams = {
            'user': self.get_user(),
            'year': datetime.now().year,
        }
        return self.render('writesms.html', tparams)

    #######################################################################################################
    ## Alertas

    @cherrypy.expose
    def alertas(self):
        tparams = {
            'user': self.get_user(),
            'year': datetime.now().year,
        }
        return self.render('alertas.html', tparams)

    #######################################################################################################
    ## Noticias

    @cherrypy.expose
    def noticias(self):
        tparams = {
            'user': self.get_user(),
            'year': datetime.now().year,
        }
        return self.render('noticias.html', tparams)

    @cherrypy.expose
    def writenew(self,local=None):
        if local != None:
            self.set_noticias(local)
            raise cherrypy.HTTPRedirect("noticias")
        else:
            tparams = {
                'user': self.get_user(),
                'year': datetime.now().year,
            }
            return self.render('writenew.html', tparams)

    @cherrypy.expose
    def draftnew(self):
        tparams = {
            'user': self.get_user(),
            'year': datetime.now().year,
        }
        return self.render('draftnew.html', tparams)

    @cherrypy.expose
    def trashnew(self):
        tparams = {
            'user': self.get_user(),
            'year': datetime.now().year,
        }
        return self.render('trashnew.html', tparams)

    @cherrypy.expose
    def publishednew(self):
        tparams = {
            'user': self.get_user(),
            'year': datetime.now().year,
        }
        return self.render('publishednew.html', tparams)

    def set_noticias(self,text):
        user = self.get_user()["username"]
        db_con = self.db_connection()
        cur = db_con.cursor()
        sql = "Insert into noticias(texto,username) values("+ text+"," + user + ")"
        cur.execute(sql)
        db_con.commit()
        cur.close()
        db_con.close()
        
    def get_noticias(self):
        noticias = []
        db_con = self.db_connection()
        cur = db_con.cursor()
        sql = "select texto,username from noticias"
        cur.execute(sql)
        data = cur.fetchone()
        for d in data:
            noticias.append((d[0],d[1]))
        cherrypy.session["noticias"] = noticias
        return cherrypy.session["noticias"]

    #####################################################################################################
    ##Eventos

    @cherrypy.expose
    def myevents(self):
        tparams = {
            'user': self.get_user(),
            'year': datetime.now().year,
        }
        return self.render('myevents.html', tparams)

    @cherrypy.expose
    def editevents(self):
        tparams = {
            'user': self.get_user(),
            'year': datetime.now().year,
        }
        return self.render('editevents.html', tparams)

    @cherrypy.expose
    def deleteevents(self):
        tparams = {
            'user': self.get_user(),
            'year': datetime.now().year,
        }
        return self.render('deleteevents.html', tparams)

    @cherrypy.expose
    def criarevento(self, nomeev=None, data=None, local=None, hora=None, nmax=None, insc=None):

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
                error = self.criarevent(nomeev, data, local, hora, nmax, insc)
                if error == "no error":
                    raise cherrypy.HTTPRedirect("/")
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

    ######################################################################################################
    ## Acesso

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

    ##################################################################################################
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
