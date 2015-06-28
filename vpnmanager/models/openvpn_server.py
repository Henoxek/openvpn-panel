import docker
import json


class ServerAlreadyExistsException(Exception):
    pass

class PortAlreadyUsedException(Exception):
    pass


class OpenVPNServer(object):

    def __init__(self, server_id=None):
        self.id = server_id
        if self.id is None:
            self.protocol = None
            self.port = None
            self.wan_routing = None
            self.running = None
            self.name = None
        else:
            self._load()

    def to_json(self):
        return json.dumps(self.as_object())

    def as_object(self):
        return {
            'id': self.id,
            'networking_info': {
                'protocol': self.protocol,
                'port': self.port,
                'wan_routing': self.wan_routing
            }
        }

    def save(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    def _load(self):
        raise NotImplementedError

    @staticmethod
    def find_all():
        raise NotImplementedError

    @staticmethod
    def find(server_id):
        raise NotImplementedError

    @property
    def clients(self):
        raise NotImplementedError

    def find_client(self, client_id):
        raise NotImplementedError