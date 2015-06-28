import docker


class OpenVPNServer(object):

    def __init__(self, server_id=None):
        self.id = server_id
        if self.id is None:
            self.port = None
            self.forward_traffic = None
            self.running = None
        else:
            self._load()

    def save(self):
        raise NotImplementedError

    def _load(self):
        raise NotImplementedError

    @staticmethod
    def findall():
        raise NotImplementedError