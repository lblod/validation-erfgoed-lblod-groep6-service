import os
from flask import Flask, request  
import traceback
from importlib import import_module
import builtins
from escape_helpers import sparql_escape

from validate import validate
import helpers
from string import Template
from helpers import query
from escape_helpers import sparql_escape_uri

# WSGI variable name used by the server
app = Flask(__name__)

##################
## Vocabularies ##
##################
mu = Namespace('http://mu.semte.ch/vocabularies/')
mu_core = Namespace('http://mu.semte.ch/vocabularies/core/')
mu_ext = Namespace('http://mu.semte.ch/vocabularies/ext/')


SERVICE_RESOURCE_BASE = 'http://mu.semte.ch/services/'

builtins.app = app
builtins.helpers = helpers
builtins.sparql_escape = sparql_escape

# Import the app from the service consuming the template
app_file = os.environ.get('APP_ENTRYPOINT')
try:
    module_path = 'ext.app.{}'.format(app_file)
    import_module(module_path)
except Exception:
    app.logger.exception('Exception raised when importing app code')


@app.route('/')
def test():
    return('We zijn in de lucht')

@app.route('/validate', methods=['GET'])
def index():
    try:	
        besluit_id = request.values['id']
        aanvraag_text = request.value['text']
        app.logger.debug("Validating " + request.values['id'] + "...")
        return(validate(besluit_id, aanvraag_text))
    except:
        app.logger.error(traceback.format_exc())
        return {'error': 'General exception'}    
        
#######################
## Start Application ##
#######################
if __name__ == '__main__':

    debug = os.environ.get('MODE') == "development"
    app.run(debug=debug, host='0.0.0.0', port=80)