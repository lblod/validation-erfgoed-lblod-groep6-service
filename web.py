import os
from flask import Flask, request  
import traceback
from importlib import import_module
import builtins
from rdflib.namespace import Namespace
from escape_helpers import sparql_escape

from string import Template
from helpers import query, logger
from escape_helpers import sparql_escape_uri

# WSGI variable name used by the server
service = Flask(__name__)

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
    helpers.logger.exception('Exception raised when importing app code')


@app.route('/')
def test():
    return('We zijn in de lucht')

@app.route('/validate', methods=['GET'])
def index():
    try:	
        my_person = "http://example.com/me"
        query_template = Template("""
        PREFIX mu: <http://mu.semte.ch/vocabularies/core/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>

        SELECT ?name
        WHERE {
            $person a foaf:Person ;
                foaf:firstName ?name .
        }
        """)
        query_string = query_template.substitute(person=sparql_escape_uri(my_person))
        query_result = query(query_string)
        return query_result
        #return(request.values['id'])
    
    except:
        service.logger.error(traceback.format_exc())
        return {'error': 'General exception'}    
        
        




#######################
## Start Application ##
#######################
if __name__ == '__main__':
    debug = os.environ.get('MODE') == "development"
    service.run(debug=debug, host='0.0.0.0', port=80)