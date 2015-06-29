from models.openvpn_server import OpenVPNServer, ServerAlreadyExistsException, PortAlreadyUsedException
from models.exceptions import ServerNotFoundException
from models.validate import RegexValidator, ArgumentValidationException

import flask
import os
import json

app = flask.Flask(__name__)

server_form_validator = RegexValidator({
    'name': r'^[a-z][a-z0-9]{2,15}$',
    'protocol': None,
    'port': None,
    'wan_routing': None
})


@app.route('/servers', methods=['GET', 'POST'])
def servers():
    if flask.request.method == 'GET':
        all_servers = OpenVPNServer.find_all()
        return flask.Response(json.dumps([srv.as_object() for srv in all_servers]),
                              status=200)
    elif flask.request.method == 'POST':
        request_body = json.loads(flask.request.data)
        try:
            request_body = server_form_validator.validate(request_body)
        except ArgumentValidationException as e:
            return flask.Response(e.message, status=400)

        srv = OpenVPNServer()
        srv.name = request_body['name']
        srv.protocol = request_body['protocol']
        if srv.protocol not in ['tcp', 'udp']:
            return flask.Response('Invalid protocol: %s' % srv.protocol, status=400)
        srv.port = int(request_body['port'])
        srv.wan_routing = bool(request_body['wan_routing'])
        try:
            srv.save()
            return flask.Response('Created', status=201)
        except ServerAlreadyExistsException:
            return flask.Response('Name conflict', status=409)
        except PortAlreadyUsedException:
            return flask.Response('Port conflict', status=409)


@app.route('/server/<server_id>', methods=['GET', 'PATCH', 'DELETE'])
def server(server_id):
    if flask.request.method == 'GET':
        try:
            srv = OpenVPNServer(server_id)
            return flask.Response(srv.to_json(), status=200)
        except ServerNotFoundException:
            return flask.Response('Server not found', status=404)
    elif flask.request.method == 'DELETE':
        try:
            srv = OpenVPNServer(server_id)
            srv.delete()
            return flask.Response('Deleted', 200)
        except ServerNotFoundException:
            return flask.Response('Server not found', status=404)
    elif flask.request.method == 'PATCH':
        request_body = json.loads(flask.request.data)
        try:
            request_body = server_form_validator.validate(request_body)
            if len(set(request_body.keys()) - {'port', 'wan_routing', 'running'}) > 0:
                return flask.Response('Bad request', status=400)
            srv = OpenVPNServer(server_id)
            srv.port = int(request_body.get('port', srv.port))
            srv.wan_routing = bool(request_body.get('wan_routing', srv.wan_routing))
            srv.running = bool(request_body.get('running', srv.running))
            srv.save()
        except ArgumentValidationException as e:
            return flask.Response(e.message, status=400)
        except PortAlreadyUsedException:
            return flask.Response('Port conflict', status=409)


@app.route('/server/<server_id>/clients', methods=['GET', 'POST'])
def server_clients(server_id):
    try:
        srv = OpenVPNServer(server_id)
    except ServerNotFoundException:
        return flask.Response('Server not found', status=404)
    if flask.request.method == 'GET':
        clients = [client.as_object() for client in srv.clients]
        return flask.Response(json.dumps(clients), status=200)
    elif flask.request.method == 'POST':
        raise NotImplementedError  # TODO: implement


@app.route('/server/<server_id>/client/<client_id>', methods=['GET', 'PATCH', 'DELETE'])
def server_client(server_id, client_id):
    raise NotImplementedError


if __name__ == '__main__':
    app.debug = bool(os.getenv('DEBUG', False))
    app.run()
