##################### Library Imports #####################

import userData
from flask import Flask, request, jsonify, abort

# -- ADINT Intermidiate Project
# -- Made by: Diogo Ferreira and Rafael Cordeiro

# ----------------------------------------
# --------------Gate Data Server----------
# ----------------------------------------


#Flask
app = Flask(__name__)


# Database endpoint for adding new gates
@app.route("/users/newuser",methods = ['POST'])
def newUserRequest():
    
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
        return jsonify({'StatusCode':'2', 'Description':'Err'})
    if status:    
        #return the secret number as JSON
        return jsonify({'StatusCode':'1','Description':'OK'})
    else:
        # The ID already exists - Not Admitted
        userData.UpdateuserToken(int(data["user_id"]),data["token"])
        return jsonify({'StatusCode':'3','Description':'Updated Token'})


# Database endpoint for adding new gates
@app.route("/user/check",methods = ['POST'])
def CheckUser():
    #retrieve data from input JSON body 
    data = request.json
    
    try:
        int(data["istID"])
        data["token"]
    except:
        abort(400)    

    if userData.CheckuserID(int(data["istID"])) and userData.CheckuserToken(data["token"]):
        return jsonify({'StatusCode':'1', 'Description':'OK'})
    else:
        return jsonify({'StatusCode':'2','Description':'Err'})


# Database endpoint for adding new gates
@app.route("/user/<path:istID>/updateCode",methods = ['POST'])
def UpdateUserCode(istID):
    #retrieve data from input JSON body 
    data = request.json
    
    try:
        int(data["istID"])
        data["token"]
        data["secret"]
    except:
        abort(400)   

    Status = userData.UpdateuserSecret(int(data["istID"]),data["secret"])
    if Status:
        return jsonify({'StatusCode':'1', 'Description':'OK'})
    else:
        return jsonify({'StatusCode':'2','Description':'Err'})



@app.route("/user/bycode")
def CheckbyCode():
    data = request.json

    try:
        data['code']
    except:
        abort(400)

    user = userData.GetUserbyAC(data['code'])

    if user:
        return jsonify({'userID': user.id})
    else:
        return jsonify({})

#Start server
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8001, debug=True)
