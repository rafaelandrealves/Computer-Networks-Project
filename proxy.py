import requests

URL_DB_gates_hist = "http://localhost:8002/gate/occurrences/"
URL_DB_gates = "http://localhost:8003/gate/"
URL_DB_gates_hist_rep = "http://localhost:8004/gate/occurrences/"
URL_DB_gates_rep = "http://localhost:8005/gate/"

def listgates():
    try:
        Gates_list=requests.get(URL_DB_gates + "listGates", allow_redirects=True).json()
    except:
        Gates_list=requests.get(URL_DB_gates_rep + "listGates", allow_redirects=True).json()
    return Gates_list


def creategates(gateID,gateLocation):
    url1 = URL_DB_gates + "newGates"
    url2 = URL_DB_gates_rep + "newGates"

    aux1 = requests.post(url1,json={'gateID':gateID,'gateLocation':gateLocation}, allow_redirects=True)
    aux2 = requests.post(url2,json={'gateID':gateID,'gateLocation':gateLocation}, allow_redirects=True)
    
    if aux1.json()['StatusCode'] == '1' and aux2.json()['StatusCode'] == '1':
        return aux1.json()['SecretNumber']
    elif aux1.json()['StatusCode'] == '3' or aux2.json()['StatusCode'] == '3':
        return '4'    
    elif aux1.json()['StatusCode'] == '1':
        return '2'
    elif  aux2.json()['StatusCode'] == '1':
        return '3'
    else:
        return '0'

def updateAct(gateID):

    aux1 = requests.get(URL_DB_gates + gateID + "/admission",allow_redirects=True)
    aux2 = requests.get(URL_DB_gates_rep + gateID + "/admission",allow_redirects=True)

    if aux1.json()['StatusCode'] == '1' and aux2.json()['StatusCode'] == '1':
        return 1
    elif aux1.json()['StatusCode'] == '1':
        return 2
    elif  aux2.json()['StatusCode'] == '1':
        return 3
    else:
        return 0



def checkgates(gateID,gateSecret):
    try:                  
        res = requests.get(URL_DB_gates+"GateSecret/"+gateID, allow_redirects=True, json={"secret": gateSecret}).json()
    except:
        res = requests.get(URL_DB_gates_rep+"GateSecret/"+gateID, allow_redirects=True, json={"secret": gateSecret}).json()
    return res


def gateshistory():
    try:                  
        res = requests.get(URL_DB_gates_hist + "history", allow_redirects=True).json()
    except:
        res = requests.get(URL_DB_gates_hist_rep + "history", allow_redirects=True).json()
    return res



def gateshistorybyID(gateID):
    try:                  
        res= requests.get(URL_DB_gates_hist + str(gateID) + "/history", allow_redirects=True).json()
    except:
        res= requests.get(URL_DB_gates_hist_rep + str(gateID) + "/history", allow_redirects=True).json()
    return res

def newGateOcco(gateID,status):

    aux1 = requests.post(URL_DB_gates_hist+"newOccurrence",json={'gate_id':gateID,'Status':status},allow_redirects=True)
    aux2 = requests.post(URL_DB_gates_hist_rep+"newOccurrence",json={'gate_id':gateID,'Status':status},allow_redirects=True)

    if aux1.json()['StatusCode'] == '1' and aux2.json()['StatusCode'] == '1':
        return 1
    elif aux1.json()['StatusCode'] == '1':
        return 2
    elif  aux2.json()['StatusCode'] == '1':
        return 3
    else:
        return 0