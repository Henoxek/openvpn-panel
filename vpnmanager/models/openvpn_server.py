import docker
import json
from pymongo import MongoClient
from bson.objectid import ObjectId
from exceptions import ServerNotFoundException


db = MongoClient().vpnmanager
db.servers.ensure_index('name', unique=True)
db.servers.ensure_index('is_deleted')
db.events.ensure_index('type')


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
        if self.id is None:
            _id = db.servers.insert({
                'name': self.name,
                'protocol': self.protocol,
                'port': self.port,
                'wan_routing': self.wan_routing,
                'running': self.running,
                'is_deleted': False
            })
            self.id = str(_id)
            db.events.insert({
                'type': 'create_server',
                'server_id': _id
            })
        else:
            raise NotImplementedError

    def delete(self):
        if self.id is None:
            db.servers.update({'_id': ObjectId(self.id)}, {
                '$set': {'is_deleted': True}
            })

    def _load(self):
        srv = db.servers.find_one({'$and': [{'_id': ObjectId(self.id)},
                                            {'is_deleted': False}]})
        if srv is None:
            raise ServerNotFoundException(self.id)
        self.protocol = srv['protocol']
        self.port = srv['port']
        self.wan_routing = srv['wan_routing']
        self.running = srv['running']
        self.name = srv['name']

    @staticmethod
    def find_all():
        srvs = [srv for srv in db.servers.find({'is_deleted': False})]
        return [OpenVPNServer(str(srv['_id'])) for srv in srvs]

    @staticmethod
    def find(server_id):
        srv = db.servers.find_one({'$and': [{'is_deleted': False},
                                            {'_id': ObjectId(server_id)}]
                                   })
        if srv is None:
            raise ServerNotFoundException(server_id)
        return OpenVPNServer(srv['_id'])

    @property
    def clients(self):
        raise NotImplementedError

    def find_client(self, client_id):
        raise NotImplementedError