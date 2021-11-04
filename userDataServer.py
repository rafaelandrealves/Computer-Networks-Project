##################### Library Imports #####################

import userData
import userHistory
from flask import Flask, request, jsonify, abort
from random import randint
import datetime

# -- ADINT Intermidiate Project
# -- Made by: Diogo Ferreira and Rafael Cordeiro

# ----------------------------------------
# --------------Gate Data Server----------
# ----------------------------------------


#Flask
app = Flask(__name__)

#Data Base Connections
# 

#Data Base Connections
# @app.route("/users",methods = ['GET'])
# def listGatesRequest():
#     # Call a query to list the active gates
#     try:
#         Gates_list = userData.()
#         result = [{'ID':item.id,'Location':item.location,'Secret Number':item.secret_number,'Activations Number':item.activation_number} for item in Gates_list]
#     except:
#         return jsonify({'Gates':'', 'StatusCode':'2', 'Description':'Err'})
        
#     return jsonify({'Gates':result,'StatusCode':'1','Description':'OK'})

# Database endpoint for adding new gates
@app.route("/users/newuser",methods = ['POST'])
def newGatesRequest():
    # Create a random Secret number to be associated to the new gate to be registered
    # secret_number = randint(1,2020210)
    # while(userData.SecretExist(secret_number)):
    #     secret_number = randint(1,2020210)
    
    #retrieve data from input JSON body 
    data = request.json
    
    try:
        int(data["user_id"])
        data["token"]
        data["secret_code"]
    except:
        abort(400)

    # Call query in GateData to create a new gate and add it do the database
    try:     
        status = userData.newUser(int(data["user_id"]),data["token"],data["secret_code"])
    except:
        return jsonify({'Secret Number':'', 'StatusCode':'2', 'Description':'Err'})
    if status:    
        #return the secret number as JSON
        return jsonify({'Secret Number':data["secret_code"],'StatusCode':'1','Description':'OK'})
    else:
        # The ID already exists - Not Admitted
        return jsonify({'Secret Number':'','StatusCode':'3','Description':'NA'})


@app.route("/occurrences/history",methods = ['GET'])
def listHistRequest():
    # Call a query to list the active gates
    User_list = userHistory.getuserHistory()
    result1 = [{'id_user_occurence':item.id_user_occurence,'user':item.user,'gate_id':item.gate_id,'Date':item.Date} for item in User_list]
    # print(result1)
    result = {"history": result1}
    # print(result)
    return result
        
    # return jsonify({'Gates':result,'StatusCode':'1','Description':'OK'})

# Database endpoint for adding new gates´
@app.route("/occurrences/newOccurrence",methods = ['POST'])
def newOccurrenceRequest():
    
    #retrieve data from input JSON body 
    data = request.json
    
    try:
        int(data["id_user_occurence"])
        data["user"]
        int(data["gate_id"])
    except:
        abort(400)

    # Call query in userData to create a new gate and add it do the database
    try:     
        status = userHistory.newOcurrence(int(data["id_user_occurence"]),data["user"],int(data["gate_id"]),datetime.datetime.now())
    except:
        return jsonify({'Secret Number':'', 'StatusCode':'2', 'Description':'Err'})
    if status:    
        #return the secret number as JSON
        return jsonify({'Secret Number':int(data["id_user_occurence"]),'StatusCode':'1','Description':'OK'})
    else:
        # The ID already exists - Not Admitted
        return jsonify({'Secret Number':'','StatusCode':'3','Description':'NA'})



#Start server
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8001, debug=True)
