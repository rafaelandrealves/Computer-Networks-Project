##################### Library Imports #####################

import userHistory
from flask import Flask, request, jsonify, abort
import datetime

# -- ADINT Final Project
# -- Made by: Diogo Ferreira and Rafael Cordeiro

# ----------------------------------------
# --------------User History Server-------
# ----------------------------------------


#Flask
app = Flask(__name__)

@app.route("/user/occurrences/history",methods = ['GET'])
def listHistRequest():

    User_list = userHistory.getuserHistory()
    result1 = [{'id_user_occurence':item.id_user_occurence,'user':item.user,'gate_id':item.gate_id,'Date':item.Date} for item in User_list]

    return jsonify({"history": result1})



@app.route("/user/occurrences/<path:istID>/history",methods = ['GET'])
def listUserHistRequest(istID):

    User_list = userHistory.GetUserOccurrences(istID)
    result1 = [{'id_user_occurence':item.id_user_occurence,'user':item.user,'gate_id':item.gate_id,'Date':item.Date} for item in User_list]

    return jsonify({"history": result1})
        
# Database endpoint for adding new occurrences
@app.route("/user/occurrences/newOccurrence",methods = ['POST'])
def newOccurrenceRequest():
    
    #retrieve data from input JSON body 
    data = request.json
    
    try:
        data["user"]
        int(data["gate_id"])
    except:
        abort(400)


    try:     
        status = userHistory.newOcurrence(data["user"],int(data["gate_id"]),datetime.datetime.now())
    except:
        return jsonify({'StatusCode':'2', 'Description':'Err'})
    if status:    

        return jsonify({'StatusCode':'1','Description':'OK'})
    else:
        return jsonify({'StatusCode':'3','Description':'NA'})


#Start server
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
