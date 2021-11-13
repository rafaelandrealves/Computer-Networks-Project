##################### Library Imports #####################

import gateHistoryReplica
from flask import Flask, request, jsonify, abort
import datetime

# -- ADINT Final Project
# -- Made by: Diogo Ferreira and Rafael Cordeiro

# ----------------------------------------
# -----Gate History Server Replica--------
# ----------------------------------------


#Flask
app = Flask(__name__)

@app.route("/gate/occurrences/history",methods = ['GET'])
def listHistRequest():

    User_list = gateHistoryReplica.getgateHistory()
    result1 = [{'id_gate_occurence':item.id_gate_occurence,'gate_id':item.gate_id,'Status':item.Status,'Date':item.Date} for item in User_list]

    return jsonify({"history": result1})
        

@app.route("/gate/occurrences/<path:gateID>/history",methods = ['GET'])
def listGateHistRequest(gateID):

    User_list = gateHistoryReplica.GetGateOccurrences(gateID)
    result1 = [{'id_gate_occurence':item.id_gate_occurence,'gate_id':item.gate_id,'Status':item.Status,'Date':item.Date} for item in User_list]

    return jsonify({"history": result1})
        


@app.route("/gate/occurrences/newOccurrence",methods = ['POST'])
def newOccurrenceRequest():
    
    #retrieve data from input JSON body 
    data = request.json
    
    try:
        int(data["gate_id"])
        data["Status"]
    except:
        abort(400)

    # Call query in userData to create a new gate and add it do the database
    try:     
        status = gateHistoryReplica.newOcurrence(int(data["gate_id"]),data["Status"],datetime.datetime.now())
    except:
        return jsonify({'StatusCode':'2', 'Description':'Err'})
    if status:    
        #return the secret number as JSON
        return jsonify({'StatusCode':'1', 'Description':'OK'})
    else:
        # The ID already exists - Not Admitted
        return jsonify({'StatusCode':'3', 'Description':'ID Already Exists'})


#Start server
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8004, debug=True)
