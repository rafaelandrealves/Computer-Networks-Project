#!/usr/bin/python

##################### Library Imports #####################

from sys import argv
import requests
from time import sleep

# -- ADINT Intermidiate Project
# -- Made by: Diogo Ferreira and Rafael Cordeiro

# ----------------------------------------
# --------------Gate App------------------
# ----------------------------------------


GATE_STATE = 0 #0 - closed / 1 - open
URL_SERVER = 'http://localhost:8000'

if len(argv) != 3:
    print("Number of arguments is not correct!")
else:
    print("Connecting to server...")
    
    #Check if secret number is valid
    CheckSecretNum = requests.get(URL_SERVER+"/Secret",allow_redirects=True, json={"secret": argv[2], "id": argv[1]}).json()
    if int(CheckSecretNum['Valid']):
        print("The secret is valid for this gate")
        
        while True :
            #get and send user code to server
            usercode = input("Type the user code: ")
            valid = requests.get(URL_SERVER+"/Usercode", allow_redirects=True, json={"code": str(usercode),"secret": argv[2],"id": argv[1]})

            #check if the gate is to open or not
            if valid.json()['valid'] == 'T':
                print("!!! CODE VALID !!!")
                GATE_STATE = 1
                print("!!! The gate will close in 5 seconds !!!")
                sleep(5)
                break
            else:
                print("!!! CODE IS NOT VALID !!!")
    else:
        print('The secret is not valid for this gate')
        print('Exiting...')
        exit()

