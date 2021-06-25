from flask import Flask
from configparser import RawConfigParser
from restconfig.blueprint import construct_restconfig_blueprint
from restconfig.connection import ConfigParserConnection

config = RawConfigParser()
config.add_section('TEST')
config['TEST']['val1'] = "42"
cpc = ConfigParserConnection(config)
app = Flask(__name__)
app.register_blueprint(construct_restconfig_blueprint(cpc), url_prefix='/config')
