import functools
from configparser import SectionProxy, RawConfigParser, NoOptionError, NoSectionError
from flask import Blueprint, request, jsonify, make_response, Response, Request
from .connection import Connection


def construct_restconfig_blueprint(_config: Connection) -> Blueprint:
    restconfig = Blueprint("restconfig", __name__)

    @restconfig.route("", methods=['GET'], strict_slashes=False)
    def send_root():
        message = 'ok'
        data = {}
        config = _config
        data['default_section'] = config.default_section()
        data['sections'] = config.sections()
        return make_response(jsonify({'message': message, 'data': data}), 200)

    @restconfig.route("section/<section>", methods=['GET'], strict_slashes=False)
    def get_section(section: str):

        config = _config
        if not config.has_section(section):
            return make_response(jsonify({'message': 'no such section', 'data': {}}), 404)

        message = 'ok'
        data = {'section': section, 'options': config.get_section(section)}
        payload = {'message': message, 'data': data}
        return make_response(jsonify(payload), 200)

    @restconfig.route("defaults", methods=['GET'], strict_slashes=False)
    def get_defaults():
        config = _config
        data = dict(config.defaults())
        message = 'ok'
        return make_response(jsonify({'message': message, 'data': data}))

    @restconfig.route("section/<section>/option/<option>", methods=['GET'], strict_slashes=False)
    def get_option(section: str, option: str):
        config = _config
        if not config.has_section(section):
            return make_response(jsonify({'message': 'no such section', 'data': {}}), 404)
        if not config.has_option(section, option):
            return make_response(jsonify({'message': 'no such option', 'data': {}}), 404)
        message = 'ok'
        data = {'section': section, 'option': config.get_option(section, option)}
        payload = {'message': message, 'data': data}
        return make_response(jsonify(payload), 200)

    return restconfig
