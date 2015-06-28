import flask
import os


app = flask.Flask(__name__)


@app.route('/servers', methods=['GET', 'POST'])
def servers():
    pass


@app.route('/server/<int:server_id>', methods=['GET', 'PATCH', 'DELETE'])
def server(server_id):
    pass


@app.route('/server/<int:server_id>/clients', methods=['GET', 'POST'])
def server_clients(server_id):
    pass


@app.route('/server/<int:server_id>/client/<client_id>', methods=['GET', 'PATCH', 'DELETE'])
def server_client(server_id, client_id):
    pass


if __name__ == '__main__':
    app.debug = bool(os.getenv('DEBUG', False))
    app.run()
