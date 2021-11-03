##################### Library Imports #####################

import requests
from flask import Flask, request, jsonify, abort,render_template,render_template_string, redirect, url_for,session
# from werkzeug.utils import redirect
from requests_oauthlib import OAuth2Session
from flask.json import jsonify
import os
# -- ADINT Intermidiate Project
# -- Made by: Diogo Ferreira and Rafael Cordeiro

# ----------------------------------------
# --------------User APP------------------
# ----------------------------------------



#Flask
app = Flask(__name__)



# This information is obtained upon registration of a new GitHub OAuth
# application here: https://github.com/settings/applications/new
client_id = "570015174623402"
client_secret = "uKU28VqDtiTGm1j51+FkjFwxOiBqMjU4DEVBeWyrzHZ+7VhdWcfQc+A1oaYmow2QMKDa/bsoQb6Gvf+/MD0eHw=="
authorization_base_url = 'https://fenix.tecnico.ulisboa.pt/oauth/userdialog'
token_url = 'https://fenix.tecnico.ulisboa.pt/oauth/access_token'

Authentifed = False

# Check the Secret Number// IF NOT REDIRECT TO LOGIN 
# User authen leva o secret e confirmar com o sistema
# Se sim, alterar authentified com global authentified = True e redirect para user
# Condição para Authentified = FALSE?
@app.route("/user",methods = ['POST', 'GET'])
def user():
    
    if Authentifed:
        return app.send_static_file("qrgen.html")
    else:
        return redirect(url_for('.demo'))


@app.route("/user/authentified/<path:secret>")
def userAuth(secret):
    # print(secret)
    # print(str(app.secret_key))
    if str(secret) == str(app.secret_key):
    # if True:
        global Authentifed 
        Authentifed = True
        return redirect(url_for('.user'))
    else: 
        abort(404)



  
@app.route("/login")
def demo():
    """Step 1: User Authorization.

    Redirect the user/resource owner to the OAuth provider (i.e. Github)
    using an URL with a few key OAuth parameters.
    """
    github = OAuth2Session(client_id, redirect_uri="http://localhost:5000/callback")
    authorization_url, state = github.authorization_url(authorization_base_url)


    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    return redirect(authorization_url)


# Step 2: User authorization, this happens on the provider.

@app.route("/callback", methods=["GET"])
def callback():
    """ Step 3: Retrieving an access token.

    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """

    print("CALLABACK")

    print(request.url)
    github = OAuth2Session(client_id, redirect_uri="http://localhost:5000/callback")
    print(github.authorized)
    token = github.fetch_token(token_url, client_secret=client_secret,
                               authorization_response=request.url)

    # At this point you can fetch protected resources but lets save
    # the token and show how this is done from a persisted token
    # in /profile.
    session['oauth_token'] = token

    return redirect(url_for('.profile'))


@app.route("/profile", methods=["GET"])
def profile():
    """Fetching a protected resource using an OAuth 2 token.
    """
    github = OAuth2Session(client_id, token=session['oauth_token'])
    # try:
    Info = jsonify(github.get('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person').json())
    # messages = {'Authentified':True,'Secret Key':app.secret_key}
    # return  redirect(url_for('.user', message = messages))
    return redirect(url_for('.userAuth',secret = str(app.secret_key)))
    # except:
    #     # messages = {'Authentified':True,'Secret Key':app.secret_key}
    #     # return redirect(url_for('.user', message = messages))
    #     return jsonify(github.get('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person').json())



#Start server
if __name__ == "__main__":
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"

    app.secret_key = os.urandom(24)
    app.run(debug=True)
