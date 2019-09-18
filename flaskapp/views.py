import adal
import flask
import uuid
import requests
import config
import os

from . import app
app.debug = True
app.secret_key = 'development'

env = os.environ['FLASK_ENV']
PORT = 5000  # A flask app by default runs on PORT 5000
if (env == 'production'):
    sitename = os.environ['WEBSITE_SITE_NAME']
    base_url = 'https://{}.azurewebsites.net'.format(sitename)
else:
    base_url = 'http://localhost:{}'.format(PORT)

AUTHORITY_URL = config.AUTHORITY_HOST_URL + '/' + config.TENANT
REDIRECT_URI = '{}/getAToken'.format(base_url)
TEMPLATE_AUTHZ_URL = ('http://login.microsoftonline.com/{}/oauth2/authorize?' +
                      'response_type=code&client_id={}&redirect_uri={}&' +
                      'state={}&resource={}')


@app.route("/")
def main():
    login_url = '{}/login'.format(base_url)
    resp = flask.Response(status=307)
    resp.headers['location'] = login_url
    return resp


@app.route("/login")
def login():
    auth_state = str(uuid.uuid4())
    flask.session['state'] = auth_state
    authorization_url = TEMPLATE_AUTHZ_URL.format(
        config.TENANT,
        config.CLIENT_ID,
        REDIRECT_URI,
        auth_state,
        config.RESOURCE)
    resp = flask.Response(status=307)
    resp.headers['location'] = authorization_url
    return resp


@app.route("/getAToken")
def main_logic():
    code = flask.request.args['code']
    state = flask.request.args['state']
    if state != flask.session['state']:
        raise ValueError("State does not match")
    auth_context = adal.AuthenticationContext(AUTHORITY_URL)
    token_response = auth_context.acquire_token_with_authorization_code(code, REDIRECT_URI, config.RESOURCE,
                                                                        config.CLIENT_ID, config.CLIENT_SECRET)
    # It is recommended to save this to a database when using a production app.
    flask.session['access_token'] = token_response['accessToken']
    flask.session['full_token'] = token_response
    return flask.redirect('/tokendetails')

@app.route('/tokendetails')
def tokendetails():
    if 'access_token' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    return flask.render_template('display_token_info.html', token_data=flask.session['full_token'])
    
@app.route('/graphcall')
def graphcall():
    if 'access_token' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    endpoint = config.RESOURCE + '/' + config.API_VERSION + '/me/'
    http_headers = {'Authorization': 'Bearer ' + flask.session.get('access_token'),
                    'User-Agent': 'adal-python-sample',
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'client-request-id': str(uuid.uuid4())}
    graph_data = requests.get(endpoint, headers=http_headers, stream=False).json()
    return flask.render_template('display_graph_info.html', graph_data=graph_data)


