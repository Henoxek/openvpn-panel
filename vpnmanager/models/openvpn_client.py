import json


class OpenVPNClient(object):

    def __init___(self, client_id=None):
        self.id = client_id
        if self.id is None:
            self.server_id = None
            self.certificate = None
        else:
            self._load()

    def to_json(self):
        return json.dumps(self.as_object())

    def as_object(self):
        return {
            'id': self.id,
            'server_id': self.server_id,
            'certificate': self.certificate
        }

    def save(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    def _load(self):
        raise NotImplementedError

    @staticmethod
    def find(server_id, client_id):
        raise NotImplementedError

    @staticmethod
    def find_all(server_id):
        raise NotImplementedError