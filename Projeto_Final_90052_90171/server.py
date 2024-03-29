
##################### Library Imports #####################

from logging import warning
from flask import Flask, request, jsonify, abort,render_template,render_template_string, redirect, url_for,session
from random import randrange
from requests_oauthlib import OAuth2Session
import json
import requests
import os
from configparser import ConfigParser
from proxy import *
import warnings
# -- ADINT Final Project
# -- Made by: Diogo Ferreira and Rafael Cordeiro

# ----------------------------------------
# --------------SERVER--------------------
# ----------------------------------------




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
    data.read(os.path.dirname(os.path.realpath(__file__)) + file)

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
    table = """{%  extends 'layout.html' %}
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
        return render_template("badlogin.html")

    res = checkgates(data.get('gateID'),data.get('gateSecret'))
    if res["Valid"]=='1':
        session["gateID"] = data.get('gateID')
        session["gateSecret"] = data.get('gateSecret')
        return redirect(url_for('.gateQR',gateID = str(data.get('gateID'))))
    else:
        return render_template("badlogin.html")

# Gate Display
@app.route("/gateQR/<path:gateID>")
def gateQR(gateID):
    try:
        session["gateID"]
    except:
        return render_template("badlogin.html")
    
    if session["gateID"] == gateID:
        return app.send_static_file("qrcode.html")
    return render_template_string("THE ID AND SECRET DONT MATCH")

# QR Code Validation
@app.route("/gate_scan",methods = ['POST', 'GET'])
def gate_scan():

    data = request.get_json()
    try:
        data['qr']
        session["gateID"]
    except:
        abort(400)
    try:
        user = requests.get(URL_DB_user+"user/bycode",json={'code': data['qr']}).json()["userID"]
    except:
        aux = newGateOcco(session["gateID"],"CLOSED")

        if aux == 2:
            warnings.warn('The Backup DATABASE could not Update')
        if aux == 3:
            warnings.warn('The Main DATABASE could not Update')
        if aux == 0:
            warnings.warn('Both DATABASES could not Update')
     
        return jsonify({'open': 0})
    try:
        aux = requests.post(URL_DB_user_hist+"user/occurrences/newOccurrence",json={'user':str(user),'gate_id': session["gateID"]},allow_redirects=True).json()
    except:
        render_template("ServerShutDown.html",db = "User Occurrences Database Server")

    if aux["StatusCode"] == "1":
        aux = newGateOcco(session["gateID"],"OPEN")
        if aux == 2:
            warnings.warn('The Backup DATABASE could not Update')
        if aux == 3:
            warnings.warn('The Main DATABASE could not Update')
        if aux == 0:
            warnings.warn('Both DATABASES could not Update')

        aux = updateAct(session["gateID"])
        if aux == 2:
            warnings.warn('The Backup DATABASE could not Update')
        if aux == 3:
            warnings.warn('The Main DATABASE could not Update')
        if aux == 0:
            warnings.warn('Both DATABASES could not Update')
        return jsonify({'open': 1})
    else:
        aux = newGateOcco(session["gateID"],"CLOSED")
        if aux == 2:
            warnings.warn('The Backup DATABASE could not Update')
        if aux == 3:
            warnings.warn('The Main DATABASE could not Update')
        if aux == 0:
            warnings.warn('Both DATABASES could not Update')

    return jsonify({'open': 0}) 


#--------------------------------------------USER------------------------------------------------------------
@app.route("/user",methods = ['POST', 'GET'])
def user():
    return redirect(url_for('.demo'))

# QR code generation
@app.route("/user/code/<path:istID>",methods = ['POST', 'GET'])
def UserQR(istID):
    try:
        session["token"]
    except:
        return render_template("badlogin.html")
    flag = 1
    if request.environ["HTTP_REFERER"] ==('http://localhost:5000/user/code/'+istID):
        flag = 0

    try:
        aux = requests.post(URL_DB_user+"user/check",json={'istID':istID,'token':session["token"]},allow_redirects=True)
    except:
        return render_template("ServerShutDown.html",db = "User Database Server")

    if aux.json()['StatusCode'] == '1':
        if flag :
            session["usercode"] = randalph(10)
            Update_Status = requests.post(URL_DB_user+"/user/"+istID+"/updateCode",json={'istID':istID,'token':session["token"],'secret':session["usercode"]},allow_redirects=True)
            if Update_Status.json()['StatusCode'] == '2':
                return render_template("badlogin.html")

        # Check if the seecret is correct with the user that is being addressed
        return render_template("qrgen.html", code=session["usercode"], istID = istID), 201
    else:
        return render_template_string('Credentials don\'t match!')

#User History
@app.route("/user/code/<path:istID>/history",methods = ['POST', 'GET'])
def user_history(istID):

    try:
        session["token"]
    except:
        return render_template("badlogin.html")

    # Check if the token is correct with the user that is being addressed
    try:
        aux = requests.post(URL_DB_user+"user/check",json={'istID':istID,'token':session["token"]},allow_redirects=True)
    except:
        render_template("ServerShutDown.html",db = "User Database Server")

    if aux.json()['StatusCode'] == '2':
        return render_template("badlogin.html")

    return render_template("table.html", istID = istID), 201


# returns a list of occurrences
@app.route("/User_reg")
def table_users():
    try:
        aux = requests.post(URL_DB_user+"user/check",json={'istID':session["userID"],'token':session["token"]},allow_redirects=True)
    except:
        return jsonify([])

    if aux.json()['StatusCode'] == '2':
        return jsonify([])

    try:
        list = requests.get(URL_DB_user_hist+"user/occurrences/"+ session["userID"]+"/history",allow_redirects=True).json()
    except:
        return jsonify([])
 
    
    return list  


#-------------------------------------------------------------AUTH-------------------------------------------
@app.route("/user/authentified/<path:istID>")
def userAuth(istID):
    try:
        session["token"]
    except:
        return render_template("badlogin.html")
    try:
        aux = requests.post(URL_DB_user+"user/check",json={'istID':istID,'token':session["token"]},allow_redirects=True)
    except:
        return render_template("ServerShutDown.html",db = "User Database Server")
    if aux.json()['StatusCode'] == "2":
        abort(404)

    if int(istID) in ADMIN:
        return redirect(url_for('.ClientIndex',istID = istID))
    else:    
        return redirect(url_for('.userIndex',istID = istID))

# User Interface
@app.route("/user/<path:istID>")
def userIndex(istID):
    try:
        int(istID)
        session["token"]
    except:
        return render_template("badlogin.html")
    try:
        aux = requests.post(URL_DB_user+"user/check",json={'istID':istID,'token':session['token']},allow_redirects=True)
    except:
        return render_template("ServerShutDown.html",db = "User Database Server")
    if aux.json()['StatusCode'] == '1':
        return render_template("IndexUser.html",istID = istID)
    else:
        return render_template("badlogin.html")


#-----------------------------------------------ADMIN----------------------------------------------------------
# Admin Interface
@app.route("/Admin")
def AdminHome():
    return redirect(url_for('.demo'))

# Admin Interface
@app.route("/Admin/<path:istID>")
def AdminIndex(istID):
    try:
        int(istID)
        session["token"]
    except:
        return render_template("badlogin.html")
    if int(istID) in ADMIN:
        try:
            aux = requests.post(URL_DB_user+"user/check",json={'istID':istID,'token':session['token']},allow_redirects=True)
        except:
            return render_template("ServerShutDown.html",db = "User Database Server")

        if aux.json()['StatusCode'] == '1':
            return render_template("indexAdmin.html",istID = istID)
        else:
            return render_template("badlogin.html")
    return render_template("notadmin.html")

# Client Interface
@app.route("/<path:istID>")
def ClientIndex(istID):
    try:
        int(istID)
        session["token"]
    except:
        return render_template("badlogin.html")
    if int(istID) in ADMIN:
        try:
            aux = requests.post(URL_DB_user+"user/check",json={'istID':istID,'token':session['token']},allow_redirects=True)
        except:
            return render_template("ServerShutDown.html",db = "User Database Server")
        if aux.json()['StatusCode'] == '1':
            return render_template("ClientIndex.html",istID = istID)
        else:
            return render_template("badlogin.html")
    return render_template("notadmin.html")

# List the Active Gates
@app.route("/Admin/<path:istID>/Gates")
def AdminGates(istID):
    try:
        int(istID)
        session["token"]
    except:
        return render_template("badlogin.html")
    try:
        aux = requests.post(URL_DB_user+"user/check",json={'istID':istID,'token':session['token']},allow_redirects=True)
    except:
        return render_template("ServerShutDown.html",db = "User Database Server")
    if aux.json()['StatusCode'] == '1':
        if int(istID) in ADMIN:
            Gates_list=listgates()
            if Gates_list["StatusCode"] == '1' and Gates_list["Gates"]:
                return render_template_string(teste_table(Gates_list["Gates"],0),istID = istID)
            else:
                return render_template_string(teste_table([],1),istID = istID)
        return render_template("notadmin.html")
    else:
        return render_template("badlogin.html")

# List the Gates History
@app.route("/Admin/<path:istID>/GatesHistory")
def AdminGatesHist(istID):
    try:
        int(istID)
        session["token"]
    except:
        return render_template("badlogin.html")

    try:
        aux = requests.post(URL_DB_user+"user/check",json={'istID':istID,'token':session['token']},allow_redirects=True)
    except:
        return render_template("ServerShutDown.html",db = "User Database Server")

    if aux.json()['StatusCode'] == '1':
        if int(istID) in ADMIN:
            l = gateshistory()

            if l["history"]:
                return render_template_string(teste_table(l["history"],0),istID = istID)
            else:
                return render_template_string(teste_table([],1),istID = istID)
        return render_template("notadmin.html") 
    else:
        return render_template("badlogin.html")

# List the Gates History
@app.route("/Admin/<path:istID>/GatesHistory/<path:gateID>")
def AdminGateHist(istID, gateID):
    try:
        int(istID)
        session["token"]
    except:
        return render_template("badlogin.html")
    try:
        aux = requests.post(URL_DB_user+"user/check",json={'istID':istID,'token':session['token']},allow_redirects=True)
    except:
        return render_template("ServerShutDown.html",db = "User Database Server")
    if aux.json()['StatusCode'] == '1':
        if int(istID) in ADMIN:
            l = gateshistorybyID(gateID)
            if l["history"]:
                return render_template_string(teste_table(l["history"],0),istID = istID)
            else:
                return render_template_string(teste_table([],1),istID = istID)
        return render_template("notadmin.html")
    else:
        return render_template("badlogin.html")
        
# Add a new gate
@app.route("/Admin/<path:istID>/newGate",methods = ['POST', 'GET'])
def AdminNewGate(istID):
    try:
        int(istID)
        session["token"]
    except:
        return render_template("badlogin.html")
    try:
        check = requests.post(URL_DB_user+"user/check",json={'istID':istID,'token':session["token"]},allow_redirects=True)
    except:
        return render_template("ServerShutDown.html",db = "User Database Server")

    if check.json()['StatusCode'] == '1':
        if int(istID) in ADMIN:
            if request.method == 'POST':
                data = request.form
                try:
                    data["gateID"]
                    data["gateLocation"]
                except:
                    return render_template("showCreated.html",message='Input information may be missing!',istID = istID)
                

                if not (data["gateID"] and data["gateID"].isdigit()):
                    if not data["gateLocation"]:
                        return render_template("showCreated.html",message='ID and Location were not correctly placed!',istID = istID)
                    return render_template("showCreated.html",message='ID was not correctly placed (must be an integer)!',istID = istID)
                elif not data["gateLocation"]:
                    return render_template("showCreated.html",message='Location was not correctly placed (must not be empty)!',istID = istID)
                
                aux = creategates(data["gateID"],data["gateLocation"])
                if aux == '2':
                    warnings.warn('The Backup DATABASE could not Update')
                    return render_template("showCreated.html",message='The Backup DATABASE could not Update',istID = istID)
                elif aux == '3':
                    warnings.warn('The Main DATABASE could not Update')
                    return render_template("showCreated.html",message='The Main DATABASE could not Update',istID = istID)
                elif aux == '0':
                    warnings.warn('Both DATABASES could not Update')
                    return render_template("showCreated.html",message='Both DATABASES could not Update',istID = istID)
                elif aux == '4':
                    return render_template("showCreated.html",message='ID was already Taken - No Gate Created!',istID = istID)
                else:
                    new = "Gate ID: "+str(data["gateID"])+"\n, Location: "+data["gateLocation"]+"\n, Secret Number: "+str(aux)
                    return render_template("showCreated.html",message=new,istID = istID), 201
            else:
                return render_template("newGate.html",istID = istID)
        return render_template("notadmin.html")
    else:
        return render_template("badlogin.html")

#--------------------------------------------------------AUTH---------------------------------------------

@app.route("/login")
def demo():

    github = OAuth2Session(client_id, redirect_uri="http://localhost:5000/callback")
    authorization_url, state = github.authorization_url(authorization_base_url)


    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    
    return redirect(authorization_url)


# Step 2: User authorization, this happens on the provider.

@app.route("/callback", methods=["GET"])
def callback():

    github = OAuth2Session(client_id, redirect_uri="http://localhost:5000/callback")
    token = github.fetch_token(token_url, client_secret=client_secret,
                               authorization_response=request.url)

    session['oauth_token'] = token

    return redirect(url_for('.profile'))

# Obtain information needed of the user
@app.route("/profile", methods=["GET"])
def profile():

    github = OAuth2Session(client_id, token=session['oauth_token'])
    Info = jsonify(github.get('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person').json())

    ist_ID = github.get('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person').json()["username"]
    session["userID"] = str(ist_ID).strip('ist')
    session["token"] = randalph(12)
    try:
        aux = requests.post(URL_DB_user + "users/newuser",json={'user_id':session["userID"],'token':session["token"],'secret_code': ""}, allow_redirects=True).json()
    except:
        return render_template("ServerShutDown.html",db = "User Database Server")
    return redirect(url_for('.userAuth',istID=session["userID"]))
 


#Start server
if __name__ == "__main__":
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"

    ADMIN = getAdmin('/config.idk')
    
    app.secret_key = os.urandom(24)
    app.run(debug=True)
