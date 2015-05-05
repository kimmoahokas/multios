__author__ = 'Kimmo Ahokas'


class VMInstance(object):
    """
    A wrapper class for novaclient.v1_1.servers.Server
    """
    def __init__(self, openstack, server):
        """

        :param instance: novaclient.v1_1.servers.Server to be wrapped
        """
        self.openstack = openstack
        self._server = server

    @property
    def name(self):
        return self._server.name

    @property
    def id(self):
        return self._server._info['id']