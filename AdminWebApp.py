from flask import Flask, render_template, request, send_from_directory, redirect, url_for, json
from GateData import getGates,GateTable,GetGate,newGate,UpdateGateCode,DeleteGate, CheckActivationsNumber
import os
from random import randint, choice
import requests
import string

# São só 4 endpoints e Têm de ser REST - gate coms ervoço, user coms erviço, gate, ver info da gate

app = Flask(__name__)

##Dúvidas
# Falta erros e meter o secret no browser
# Admin deve ter id? Todos podem ligar?
# Activation number é o num de ativações!!
# 
# Deve ser randint ou com letras? - O que quisermos desde que seja aleatório
# NO POST junta-se o error 200 ou só retornar o secret e é como JSON?
@app.route("/Admin",methods = ['POST', 'GET'])
def AdminWebApp():
    # rand_char = choice(string.ascii_letters)
    if request.method == 'POST':
        new_gateID = request.form['gateID']
        new_gateLocation = request.form['gateLocation']
        secret_number = randint(1,2020210)
        newGate(new_gateID,new_gateLocation,secret_number,0)
        SN = {'Secret Number':secret_number}
        return json.jsonify(SN)
    else:
        Gates_list = getGates()
        result = []
        for item in Gates_list:
            dict = {'ID':item.id,'Location':item.location,'Secret Number':item.secret_number,'Activations Number':item.activation_number}
            result.append(dict)
        return json.jsonify(result)




if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)