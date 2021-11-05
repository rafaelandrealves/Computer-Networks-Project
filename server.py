
##################### Library Imports #####################

from flask import Flask, request, jsonify, abort,render_template,render_template_string, redirect, url_for,session
from random import randrange
from datetime import datetime
from requests_oauthlib import OAuth2Session
import json
import requests
import os

# -- ADINT Intermidiate Project
# -- Made by: Diogo Ferreira and Rafael Cordeiro

# ----------------------------------------
# --------------SERVER--------------------
# ----------------------------------------


# PRoblemas- Tabela não mete todas as colunas
# Falta as verificações
# A data ta só com ano,mes,dia 
# Não estou a conseguir meter passar o json com so secret

DATA = [] #list of [usercode, creation_time]
URL_DB = "http://localhost:8001/"

# This information is obtained upon registration of a new GitHub OAuth
# application here: https://github.com/settings/applications/new
client_id = "570015174623402"
client_secret = "uKU28VqDtiTGm1j51+FkjFwxOiBqMjU4DEVBeWyrzHZ+7VhdWcfQc+A1oaYmow2QMKDa/bsoQb6Gvf+/MD0eHw=="
authorization_base_url = 'https://fenix.tecnico.ulisboa.pt/oauth/userdialog'
token_url = 'https://fenix.tecnico.ulisboa.pt/oauth/access_token'

Authentifed = False

#convert int to char to create alphanumeric sequence
def int2char(n):
    return chr(65+n-43*(n//26))

#returns alphanumeric sequence with lenght n
def randalph(n):
    code=""

    for i in range(n):
        code+=int2char(randrange(36))
        
    return code


#Flask
app = Flask(__name__)

#User and Gate endpoints
@app.route("/Usercode",methods = ['POST', 'GET'])
def userCode():

    #get list of usercodes
    lcodes = [i[0] for i in DATA]

    #User app - create a new usercode
    if request.method == 'POST':
        
        #create alphanumeric sequence with length 6
        code=randalph(6)
        while code in lcodes:
            code=randalph(6)
            
        #store
        DATA.append([code, datetime.now()])
        
        #send
        return jsonify({'code': code}), 201

    #Gate app - open or not the gate
    elif request.method == 'GET':

        #get and check body
        data = request.json
        try:
            data["code"]
            int(data["id"])
            data["secret"]  
        except:
            abort(400)

        aux = requests.get(URL_DB+"/GateSecret/"+data["id"],allow_redirects=True, json={"secret": data["secret"]}).json()
        if aux['Valid']=='0':
            abort(400)
        
        if data["code"] in lcodes :
            
            #get usercode info
            ind = lcodes.index(data["code"])
            buf = DATA.pop(ind)

            #check if 60 seconds have passed since creation
            delta = datetime.now() - buf[1]
            if delta.days > 0 or delta.seconds > 60:

                #clean DATA from expired usercode
                for i in range(ind):
                    DATA.pop(0)
                return jsonify({'valid': 'F'})
            else:

                #increment on the gate table
                url = URL_DB + "/"+ str(data["id"]) + "/admission"
                requests.get(url, allow_redirects=True)
                return jsonify({'valid': 'T'})
        else:
            return jsonify({'valid': 'F'})

# Check the Secret Number
@app.route("/Secret")
def secrect():
    data = request.json
    try:
        data["secret"]
        int(data["id"])
    except:
        abort(400)

    return requests.get(URL_DB+"/GateSecret/"+data["id"],allow_redirects=True, json={"secret": data["secret"]}).json()
        
#check the remaining usercodes in DATA
@app.route("/Users")
def users():
    available = ""
    curtime = datetime.now()
    for i in DATA:
        available += (i[0] + " - " + str(curtime - i[1]) + "\n")
        
    return available

# Admin Interface
@app.route("/Admin")
def AdminHome():
    return render_template("index.html")

# List the Active Gates
@app.route("/Admin/Gates")
def AdminGates():
    url = URL_DB
    Gates_list=requests.get(url, allow_redirects=True).json()

    if Gates_list["StatusCode"] == '1':
        return render_template_string(teste_table(Gates_list["Gates"],0))
    else:
        return render_template_string(teste_table([],1))
        
# Add a new gate
@app.route("/Admin/newGate",methods = ['POST', 'GET'])
def AdminNewGate():
    if request.method == 'POST':
        data = request.form
        try:
            data["gateID"]
            data["gateLocation"]
        except:
            abort(400)
        
        url = URL_DB + "/newGates"

        if not (data["gateID"] and data["gateID"].isdigit()):
            if not data["gateLocation"]:
                return render_template("showCreated.html",message='ID and Location were not correctly placed!')
            return render_template("showCreated.html",message='ID was not correctly placed (must be an integer)!')
        elif not data["gateLocation"]:
            return render_template("showCreated.html",message='Location was not correctly placed (must not be empty)!')
        
        aux = requests.post(url,json={'gateID':data["gateID"],'gateLocation':data["gateLocation"]}, allow_redirects=True)

        if aux.json()['StatusCode'] == '3':
            return render_template("showCreated.html",message='ID was already Taken - No Gate Created!')
        elif aux.json()['StatusCode'] == '2':
            return render_template("showCreated.html",message='Database Session Failure!')
        else:
            new = "Gate ID: "+str(data["gateID"])+"\n, Location: "+data["gateLocation"]+"\n, Secret Number: "+str(aux.json()['Secret Number'])
            return render_template("showCreated.html",message=new), 201
    else:
        return render_template("newGate.html")


def teste_table(dicList,err):
    table = """{% extends 'layout.html' %}
                {% block content %}
                <body>
                <h3> List of Gates</h3>"""

    if not err:
        table += """<table border="1" class="dataframe Attendance"
                <tr><td>ID</td><td>Location</td><td>SecretNumber</td><td>ActivationsNumber</td></tr>"""
    else:
        table += "Error reaching Database"
    
    for item in dicList:
        table += ("<tr><td>" + str(item["ID"])+"</td><td>" + item["Location"] + "</td><td>" +
                  str(item["Secret Number"]) + "</td><td>" + str(item["Activations Number"]) + "</tr>\n")

    table += "</table>\n</body>\n{% endblock %}"

    return table

# Check the Secret Number// IF NOT REDIRECT TO LOGIN 
# User authen leva o secret e confirmar com o sistema
# Se sim, alterar authentified com global authentified = True e redirect para user
# Condição para Authentified = FALSE?

@app.route("/",methods = ['POST', 'GET'])
def index():
    ## TODO 3 abas a dizer se quero ser user, gate ou admin e redirecionar
    return 

## Ter um main page de logins em /user . depois para aceder as cenas ter user/ist_id/secret
# dentro disto confirmar o secret e isso se existem

@app.route("/user/code",methods = ['POST', 'GET'])
def user():
    # Tirar Authentified - Mandar sempre para a autentificação
    if Authentifed:
        return render_template("qrgen.html")
    else:
        return redirect(url_for('.demo'))

@app.route("/User_reg")
def table_users():
    return  requests.get(URL_DB+"occurrences/history",allow_redirects=True).json()

@app.route("/user/authentified/<path:secret>")
def userAuth(secret):
    # print(secret)
    # print(str(app.secret_key))
    # data = request.json
    # print(data)
    if str(secret) == str(app.secret_key):
    # if True:
        global Authentifed 
        Authentifed = True
        # COMO RECONHCER USERs ANTIGOS?
        print(app.secret_key)
        aux = requests.post(URL_DB + "users/newuser",json={'user_id':'2','token':str(app.secret_key),'secret_code':'123'}, allow_redirects=True)
        print(aux.json())
        return redirect(url_for('.user'))
    else: 
        abort(404)


# Criar um user - user id , token e qr code
# registado quando faz login no fenix - se já estiver, já está, senão adiciona
# Não é preciso autentificação - serv base de dados
# serviço cria o QR code
# Atenção ao fault tolerance das 2 réplicas
# Verificar sempre se o 1º servidor está a funcionar, caso contrário direcionar para o 2º servidor
# sergurança browser servidor é o token


# Vou tratar no user da adicionar user na base de dados e da base de dados do user
# Diogo, tratas to browser e servidor criar automaticamente um QR sempre se que dá refresh quando se acede ao user e tratas da get web app
# Admin é criar um json com os ids das pessoas que são admins
# Igual ao intermédio, trato de criar o JSON e fazer a autentificação e verificação
# O primeiro a acabar trata da réplica

# NOTA : podemos tirar foto ao QR e usar o video comot emos, o prof diz que é tchill, só atenção para explicar isso no relatório
## NA user app são todos os registos que foram bem sucedidos ou seja a gate foi aberta
## NO admin é um registo tanto de gate que foram abertas como fechadas, anonymized


# ISOLAR GATES EM VARIAS BASE DE DADOS - guar abriu abiru e data, noutra um od asspcoa, na base de dados do utilizador guardar a data e ligar por aí
# e etr uma base de dados por historial das gates que foram abertas para o admin - no historial do admin não é preciso ligação por data, basta ir por gate,
# acessed gates by user também não
# Só é preciso fazer 2 inserts "de cada vez"


@app.route("/login")
def demo():
    """Step 1: User Authorization.

    Redirect the user/resource owner to the OAuth provider (i.e. Github)
    using an URL with a few key OAuth parameters.
    """
    github = OAuth2Session(client_id, redirect_uri="http://localhost:5000/callback")
    authorization_url, state = github.authorization_url(authorization_base_url)


    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    return redirect(authorization_url)


# Step 2: User authorization, this happens on the provider.

@app.route("/callback", methods=["GET"])
def callback():
    """ Step 3: Retrieving an access token.

    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """

    print("CALLABACK")

    print(request.url)
    github = OAuth2Session(client_id, redirect_uri="http://localhost:5000/callback")
    print(github.authorized)
    token = github.fetch_token(token_url, client_secret=client_secret,
                               authorization_response=request.url)

    # At this point you can fetch protected resources but lets save
    # the token and show how this is done from a persisted token
    # in /profile.
    session['oauth_token'] = token

    return redirect(url_for('.profile'))


@app.route("/profile", methods=["GET"])
def profile():
    """Fetching a protected resource using an OAuth 2 token.
    """
    github = OAuth2Session(client_id, token=session['oauth_token'])
    # try:
    Info = jsonify(github.get('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person').json())
    # messages = {'Authentified':True,'Secret Key':app.secret_key}
    # return  redirect(url_for('.user', message = messages))
    print('AQUI')
    ist_ID = github.get('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person').json()["username"]

    data = {'token': str(app.secret_key)}
    
    return redirect(url_for('.userAuth',secret = str(app.secret_key)))
    # return redirect(url_for('.userAuth',ist_ID = 90171,json=data))
    # except:
    #     # messages = {'Authentified':True,'Secret Key':app.secret_key}
    #     # return redirect(url_for('.user', message = messages))
    #     return jsonify(github.get('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person').json())


#Start server
if __name__ == "__main__":
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"

    app.secret_key = os.urandom(24)
    app.run(debug=True)