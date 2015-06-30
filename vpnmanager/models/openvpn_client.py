from pymongo import MongoClient
from bson.objectid import ObjectId

import json

db = MongoClient().vpnmanager


class ClientNotFoundException(Exception):
    pass


class OpenVPNClient(object):

    def __init__(self, client_id=None):
        self.id = client_id
        if self.id is None:
            self.server_id = None
            self.certificate = None
            self.description = None
        else:
            self._load()

    def to_json(self):
        return json.dumps(self.as_object())

    def as_object(self):
        return {
            'id': self.id,
            'server_id': self.server_id,
            'certificate': self.certificate,
            'description': self.description
        }

    def save(self):
        if self.id is None:
            _id = db.clients.insert({
                'server_id': ObjectId(self.server_id),
                'description': self.description,
                'certificate': self.certificate,
                'is_deleted': False
            })
            self.id = str(_id)
            db.events.insert({
                'type': 'create_client',
                'client_id': _id
            })
        else:
            db.clients.update({'_id': ObjectId(self.id)}, {
                'server_id': ObjectId(self.server_id),
                'description': self.description,
                'certificate': self.certificate,
                'is_deleted': False
            })

    def delete(self):
        db.clients.update({'_id': ObjectId(self.id)}, {
            '$set': {'is_deleted': True}
        })
        db.events.insert({'type': 'delete_client',
                          'client_id': ObjectId(self.id)})

    def _load(self):
        clt = db.clients.find_one({'$and': [{'_id': ObjectId(self.id)},
                                            {'is_deleted': False}]})
        if clt is None:
            raise ClientNotFoundException(self.id)
        self.description = clt['description']
        self.server_id = clt['server_id']
        self.certificate = clt.get('certificate', None)

    @staticmethod
    def find_all(server_id):
        clts = [clt for clt in db.clients.find({'$and': [{'is_deleted': False},
                                                         {'server_id': ObjectId(server_id)}]})]
        return [OpenVPNClient(str(clt['_id'])) for clt in clts]
