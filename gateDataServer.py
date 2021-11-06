##################### Library Imports #####################

import GateData
from flask import Flask, request, jsonify, abort
from random import randint


# -- ADINT Intermidiate Project
# -- Made by: Diogo Ferreira and Rafael Cordeiro

# ----------------------------------------
# --------------Gate Data Server----------
# ----------------------------------------


#Flask
app = Flask(__name__)

#Data Base Connections
@app.route("/gate",methods = ['GET'])
def listGatesRequest():
    # Call a query to list the active gates
    try:
        Gates_list = GateData.getGates()
        result = [{'ID':item.id,'Location':item.location,'Secret Number':item.secret_number,'Activations Number':item.activation_number} for item in Gates_list]
    except:
        return jsonify({'Gates':'', 'StatusCode':'2', 'Description':'Err'})
        
    return jsonify({'Gates':result,'StatusCode':'1','Description':'OK'})

# Database endpoint for adding new gates
@app.route("/gate/newGates",methods = ['POST'])
def newGatesRequest():
    # Create a random Secret number to be associated to the new gate to be registered
    secret_number = randint(1,2020210)
    while(GateData.SecretExist(secret_number)):
        secret_number = randint(1,2020210)
    
    #retrieve data from input JSON body 
    data = request.json
    
    try:
        int(data["gateID"])
        data["gateLocation"]
    except:
        abort(400)

    # Call query in GateData to create a new gate and add it do the database
    try:     
        status = GateData.newGate(int(data["gateID"]),data["gateLocation"],secret_number,0)
    except:
        return jsonify({'Secret Number':'', 'StatusCode':'2', 'Description':'Err'})
    if status:    
        #return the secret number as JSON
        return jsonify({'Secret Number':secret_number,'StatusCode':'1','Description':'OK'})
    else:
        # The ID already exists - Not Admitted
        return jsonify({'Secret Number':'','StatusCode':'3','Description':'NA'})


# Endpoint to increase the gate activation number
@app.route("/gate/<path:id>/admission",methods = ['GET'])
def updateGatesActivation(id):
    try:
        int(id)
    except:
        abort(400)

    try:
        status = GateData.UpdateGateActCode(int(id))
    except:
        return jsonify({'StatusCode':'2', 'Description':'Err'})
    if status:
        return jsonify({'StatusCode':'1','Description':'OK'})
    else:
        return jsonify({'StatusCode':'3','Description':'Table Error, ID does not Exist'})
 
# Endpoint to Check Secret in the data base section
@app.route("/gate/GateSecret/<path:id>",methods = ['GET'])
def CheckSecret(id):
    #retrieve data from input JSON body 
    data = request.json

    try:
        int(id)
        data["secret"]
    except:
        abort(400)

    try:
        aux = GateData.CheckSecret(int(id),data["secret"])
    except:
        return jsonify({'Valid':'0'})
    if aux:
        return jsonify({'Valid':'1'})
    else:
        return jsonify({'Valid':'0'})

# Endpint to delete a specific gate
@app.route("/gate/<path:id>/inactive",methods = ['GET'])
def Deletegate(id):

    try:
        int(id)
    except:
        abort(400)
    
    try:
        status = GateData.DeleteGate(int(id))
    except:
        return jsonify({'StatusCode':'2', 'Description':'Err'})
    if status:
        return jsonify({'StatusCode':'1','Description':'OK'})
    else:
        return jsonify({'StatusCode':'3','Description':'Table Error, ID does not Exist'})



#Start server
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8003, debug=True)
