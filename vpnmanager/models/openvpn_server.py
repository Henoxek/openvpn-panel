import docker
import json
from pymongo import MongoClient
from bson.objectid import ObjectId
from exceptions import ServerNotFoundException
from openvpn_client import OpenVPNClient, ClientNotFoundException


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
            old_properties = db.servers.find({'_id': ObjectId(self.id)})
            if (old_properties['port'] != self.port) or (old_properties['protocol'] != self.protocol):
                db.events.insert({
                    'type': 'server_reconfiguration_needed',
                    'server_id': old_properties['_id']
                })
            if old_properties['wan_routing'] != self.wan_routing:
                db.events.insert({
                    'type': 'firewall_configuration_needed',
                    'server_id': old_properties['_id']
                })
            if old_properties['running'] != self.running:
                db.events.insert({
                    'type': 'running_state_changed',
                    'server_id': old_properties['_id']
                })
            db.servers.update({'_id': ObjectId(self.id)}, {
                'name': self.name,
                'protocol': self.protocol,
                'port': self.port,
                'wan_routing': self.wan_routing,
                'running': self.running,
                'is_deleted': False
            })

    def delete(self):
        db.servers.update({'_id': ObjectId(self.id)}, {
            '$set': {'is_deleted': True}
        })
        db.events.insert({
            'type': 'delete_server',
            'server_id': ObjectId(self.id)
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

    @property
    def clients(self):
        return OpenVPNClient.find_all(self.id)

    def find_client(self, client_id):
        clt = OpenVPNClient(client_id)
        if clt.server_id != self.id:
            raise ClientNotFoundException(client_id)
        if clt.server_id != self.id:
            raise ClientNotFoundException(client_id)
        return clt
