
##################### Library Imports #####################

from flask import Flask, request, jsonify, abort,render_template,render_template_string
from random import randrange
from datetime import datetime
import requests

# -- ADINT Intermidiate Project
# -- Made by: Diogo Ferreira and Rafael Cordeiro

# ----------------------------------------
# --------------SERVER--------------------
# ----------------------------------------

DATA = [] #list of [usercode, creation_time]
URL_DB = "http://localhost:8001/gate"
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


#Start server
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
