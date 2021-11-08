
##################### Library Imports #####################

from flask import Flask, request, jsonify, abort,render_template,render_template_string, redirect, url_for,session
from random import randrange
from datetime import datetime
from requests_oauthlib import OAuth2Session
import json
import requests
import os
from configparser import ConfigParser

# -- ADINT Intermidiate Project
# -- Made by: Diogo Ferreira and Rafael Cordeiro

# ----------------------------------------
# --------------SERVER--------------------
# ----------------------------------------


# TODO P
# Falta as verificações
# A data ta só com ano,mes,dia 


URL_DB_user_hist = "http://localhost:8000/"
URL_DB_user = "http://localhost:8001/"
URL_DB_gates_hist = "http://localhost:8002/gate/occurrences/"
URL_DB_gates = "http://localhost:8003/gate/"

# This information is obtained upon registration of a new GitHub OAuth
# application here: https://github.com/settings/applications/new
client_id = "570015174623402"
client_secret = "uKU28VqDtiTGm1j51+FkjFwxOiBqMjU4DEVBeWyrzHZ+7VhdWcfQc+A1oaYmow2QMKDa/bsoQb6Gvf+/MD0eHw=="
authorization_base_url = 'https://fenix.tecnico.ulisboa.pt/oauth/userdialog'
token_url = 'https://fenix.tecnico.ulisboa.pt/oauth/access_token'

type_user = 'user'

ADMIN = []

#get admins info from config file
def getAdmin(file):
    data = ConfigParser()
    data.read(file)

    return json.loads(data.get('IstGate','Admin'))

#convert int to char to create alphanumeric sequence
def int2char(n):
    return chr(65+n-43*(n//26))

#returns alphanumeric sequence with lenght n
def randalph(n):
    code=""

    for i in range(n):
        code+=int2char(randrange(36))
        
    return code

#returns HTML for table page
def teste_table(dicList,err):
    table = """{% extends 'layout.html' %}
                {% block content %}
                <body>
                <h3> List of Gates</h3>"""

    if not err:
        table += draw_table(dicList)
    else:
        table += "Empty Table Received"

    table += "</body>\n{% endblock %}"

    return table

#returns HTML for table
def draw_table(d):
    t = """<table border="1" class="dataframe Attendance">"""
    k = list(d[0].keys())
    
    t+= "<tr>"
    for i in k:
        t+= "<td>"+i+"</td>"
    t+= "</tr>\n"

    for i in d:
        t+= "<tr>"
        for j in k:
           t+= "<td>"+str(i[j])+"</td>" 
        t+= "</tr>\n"

    t += "</table>\n"
    return t

#Flask
app = Flask(__name__)

# Check the Secret Number// IF NOT REDIRECT TO LOGIN 
# User authen leva o secret e confirmar com o sistema
# Se sim, alterar authentified com global authentified = True e redirect para user
# Condição para Authentified = FALSE?


#------------------------------------------GATE--------------------------
@app.route("/",methods = ['POST', 'GET'])
def index():
    return render_template("index.html")

@app.route("/gate")
def gate():
    return render_template("gauthe.html")

@app.route("/gateAuth")
def gateAuth():
    data = request.args

    try:
        int(data.get('gateID'))
        data.get('gateSecret')
    except:
        abort(400)

    res = requests.get("http://localhost:8003/gate/GateSecret/"+str(data.get('gateID')), allow_redirects=True, json={"secret": data.get('gateSecret')}).json()
    # session['gateSecret'] = data.get('gateSecret')
    if res["Valid"]=='1':
        session["gateID"] = data.get('gateID')
        session["gateSecret"] = data.get('gateSecret')
        return redirect(url_for('.gate',gateID = str(data.get('gateID'))))
    else:
        return render_template_string("THE ID AND SECRET DONT MATCH")
    
@app.route("/gateQR/<path:gateID>")
def gateQR(gateID):
    if session["gateID"] == gateID:
        return app.send_static_file("qrcode.html")
    return render_template_string("THE ID AND SECRET DONT MATCH")


@app.route("/gate_scan")
def gate_scan():
    # FAZER
    data = request.json

    try:
        data['qr']
    except:
        abort(404)

    try:
        user = request.get(URL_DB_user+"user/bycode",json={'code': data['qr']}).json()["gateID"]
    except:
        aux = request.post(URL_DB_user_hist+"user/occurrences/newOccurrence",json={'gate_id':session["gateID"],'Status':'CLOSED'},allow_redirects=True)
        return jsonify({'open': 0})
    # Còdigo para ANALISAR Gate para abrir ou não

    # INSERÇÃO BASE DE DADOS

    aux = requests.post(URL_DB_gate_hist+"user/occurrences/newOccurrence",json={'user':str(user),'gate_id': session["gateID"]},allow_redirects=True).json()

    if aux["StatusCode"] == "1":
        aux = request.post(URL_DB_user_hist+"user/occurrences/newOccurrence",json={'gate_id':session["gateID"],'Status':'OPEN'},allow_redirects=True)
        return jsonify({'open': 1})
    else:
        aux = request.post(URL_DB_user_hist+"user/occurrences/newOccurrence",json={'gate_id':session["gateID"],'Status':'CLOSED'},allow_redirects=True)

    ## -> COLOCAR SEMPRE QUE a GATE É ABERTA -- METER O QUE VEM DO JSON
        # aux = requests.post(URL_DB_user_hist+"user/occurrences/newOccurrence",json={'id_user_occurence':??,'user':session.pop('userID'),'gate_id':??},allow_redirects=True).json()
        # aux = requests.post(URL_DB_gate_hist+"user/occurrences/newOccurrence",json={'id_gate_occurence':??,'gate_id':??,'Status':'OPEN'},allow_redirects=True).json()
    ## -> COLOCAR SEMPRE QUE a GATE NÂO É ABERTA COM Sucesso -- METER O QUE VEM DO JSON
        # aux = requests.post(URL_DB_gate_hist+"user/occurrences/newOccurrence",json={'id_gate_occurence':??,'gate_id':??,'Status':'CLOSED'},allow_redirects=True).json()

    return jsonify({'open': 0}) 


#--------------------------------------------USER------------------------------------------------------------
@app.route("/user",methods = ['POST', 'GET'])
def user():
    return redirect(url_for('.demo'))

#User and Gate endpoints
@app.route("/user/code/<path:istID>",methods = ['POST', 'GET'])
def QRcode(istID):
    usercode = randalph(10)
    session['usercode'] = usercode
    session['userID'] = istID

    #REQUEST TO USER DATABASE - send new usercode to certain token
    # TODO METER CHECK DENTRO UPDATE
    url = "http://localhost:8001/users/newuser"
    # aux = requests.post(url,json={'user_id':data["id"],'token':data["token"],'secret_code':usercode}, allow_redirects=True)
    # Check if the seecret is correct with the user that is being addressed
    aux = requests.post(URL_DB_user+"user/check",json={'istID':istID,'token':str(app.secret_key)},allow_redirects=True)


    if aux.json()['StatusCode'] == '3':
        #UPDATE SECRET CODE E ASSIM
        print()
    elif aux.json()['StatusCode'] == '2':
        return render_template_string('Database Session Failure!')

    return render_template("qrgen.html", usercode=usercode), 201


#User and Gate endpoints
@app.route("/user/code/<path:istID>/history",methods = ['POST', 'GET'])
def user_history(istID):
    usercode = randalph(10)

    #REQUEST TO USER DATABASE - send new usercode to certain token

    # aux = requests.post(url,json={'user_id':data["id"],'token':data["token"],'secret_code':usercode}, allow_redirects=True)
    # Check if the seecret is correct with the user that is being addressed
    aux = requests.post(URL_DB_user+"user/check",json={'istID':istID,'token':str(app.secret_key)},allow_redirects=True)

    if aux.json()['StatusCode'] == '3':
        #UPDATE SECRET CODE E ASSIM
        print()
    elif aux.json()['StatusCode'] == '2':
        return render_template_string('Database Session Failure!')

    return render_template("table.html"), 201



# TODO MUDAR PARA SER ESPECIFICO APENAS DE UM USER
@app.route("/User_reg")
def table_users():
    return  requests.get(URL_DB_user_hist+"user/occurrences/history",allow_redirects=True).json()


#-------------------------------------------------------------AUTH-------------------------------------------

# TODO FALTA ALTERAR O QR CODE.
@app.route("/user/authentified/<path:istID>/<path:secret>")
def userAuth(istID,secret):
    if secret == session["token"]:
        aux = requests.post(URL_DB_user + "users/newuser",json={'user_id':istID,'token':session["token"],'secret_code': ""}, allow_redirects=True)
        if int(istID) in ADMIN:
            return redirect(url_for('.AdminNewGate',istID = istID))
        else:    
            return redirect(url_for('.QRcode',istID = istID))
    else: 
        abort(404)

#-----------------------------------------------ADMIN----------------------------------------------------------
# Admin Interface
@app.route("/Admin")
def AdminHome():
    return redirect(url_for('.demo'))

# List the Active Gates
@app.route("/Admin/<path:istID>/Gates")
def AdminGates(istID):
    aux = requests.post(URL_DB_user+"user/check",json={'istID':istID,'token':str(app.secret_key)},allow_redirects=True)
    if aux.json()['StatusCode'] == '1':
        if int(istID) in ADMIN:
            Gates_list=requests.get(URL_DB_gates + "listGates", allow_redirects=True).json()

            if Gates_list["StatusCode"] == '1' and Gates_list["Gates"]:
                return render_template_string(teste_table(Gates_list["Gates"],0))
            else:
                return render_template_string(teste_table([],1))
        return render_template("notadmin.html")
    else:
        abort(404)

# List the Gates History
@app.route("/Admin/<path:istID>/GatesHistory")
def AdminGatesHist(istID):
    aux = requests.post(URL_DB_user+"user/check",json={'istID':istID,'token':str(app.secret_key)},allow_redirects=True)
    if aux.json()['StatusCode'] == '1':
        if int(istID) in ADMIN:
            l = requests.get(URL_DB_gates_hist + "history", allow_redirects=True).json()

            if l["history"]:
                return render_template_string(teste_table(l["history"],0))
            else:
                return render_template_string(teste_table([],1))
        return render_template("notadmin.html") 
    else:
        abort(404)

# List the Gates History
@app.route("/Admin/<path:istID>/GatesHistory/<path:gateID>")
def AdminGateHist(istID, gateID):
    aux = requests.post(URL_DB_user+"user/check",json={'istID':istID,'token':str(app.secret_key)},allow_redirects=True)
    if aux.json()['StatusCode'] == '1':
        if int(istID) in ADMIN:
            l = requests.get(URL_DB_gates_hist + str(gateID) + "/history", allow_redirects=True).json()

            if l["history"]:
                return render_template_string(teste_table(l["history"],0))
            else:
                return render_template_string(teste_table([],1))
        return render_template("notadmin.html")
    else:
        abort(404)
        
# Add a new gate
@app.route("/Admin/<path:istID>/newGate",methods = ['POST', 'GET'])
def AdminNewGate(istID):
    check = requests.post(URL_DB_user+"user/check",json={'istID':istID,'token':str(app.secret_key)},allow_redirects=True)
    if check.json()['StatusCode'] == '1':
        if int(istID) in ADMIN:
            if request.method == 'POST':
                data = request.form
                try:
                    data["gateID"]
                    data["gateLocation"]
                except:
                    abort(400)
                
                url = URL_DB_gates + "newGates"

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
        return render_template("notadmin.html")
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

    print("CALLBACK")

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

    ist_ID = github.get('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person').json()["username"]
    session["userID"] = str(ist_ID).strip('ist')
    session["token"] = randalph(12)
    
    return redirect(url_for('.userAuth',istID=session["userID"],secret=session["token"]))
 


#Start server
if __name__ == "__main__":
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"

    ADMIN = getAdmin('config.idk')
    
    app.secret_key = os.urandom(24)
    app.run(debug=True)
