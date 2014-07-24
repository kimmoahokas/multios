__author__ = 'Kimmo Ahokas'

import keystoneclient.v2_0.client as keystoneclient
import glanceclient.v2.client as glanceclient
import novaclient.v1_1.client as novaclient
import neutronclient.v2_0.client as neutronclient
import cinderclient.v2.client as cinderclient
import heatclient.v1.client as heatclient
import ceilometerclient.v2.client as ceilometerclient
import logging


class OpenStackInstance(object):
    """Single OpenStack instance. Contains different OpenStack endpoints and
    authentication credentials etc.
    """

    @classmethod
    def create_from_config(cls, config, lazy_load=True):
        """
        :param config: Object containing necessary OpenStack credentials
        :param lazy_load: Boolean indicating whether OpenStack service
        clients should be initialized only when used for the first time.
        Default True
        :return: new instance ot this class
        """
        # TODO: error handling

        return cls(config['name'], config['auth_url'], config['username'],
                   config['password'], config['tenant_name'],
                   config['region_name'], lazy_load)

    def __init__(self, name, auth_url, username, password, tenant_name,
                 region_name, lazy_load=True):
        """Instantiate OpenStackInstance.

        """

        self.name = name
        self.auth_url = auth_url
        self.username = username
        self.password = password
        self.tenant_name = tenant_name
        self.region_name = region_name
        # Initialize to none, connect_keystone() will populate this later
        self.auth_token = None
        self.lazy_load = lazy_load

        self.keystone = None
        self.glance = None
        self.nova = None
        self.neutron = None
        self.cinder = None
        self.ceilometer = None
        self.heat = None

        self.logger = logging.getLogger('{}{}'.format(__name__, name))
        self.connect_keystone()

        if not self.lazy_load:
            self.connect_all_optional_services()

    def connect_all_optional_services(self):
        self.connect_glance()
        self.connect_nova()
        self.connect_neutron()
        self.connect_cinder()
        self.connect_heat()
        self.connect_ceilometer()

    def connect_keystone(self):
        try:
            self.keystone = keystoneclient.Client(auth_url=self.auth_url,
                                                  username=self.username,
                                                  password=self.password,
                                                  tenant_name=self.tenant_name,
                                                  region_name=self.region_name)
            self.auth_token = self.keystone.auth_token
        except Exception as e:
            raise e
        self.logger.info('keystone connected')

    def connect_glance(self):
        glance_endpoint = self.keystone.service_catalog.url_for(
            service_type='image')
        self.glance = glanceclient.Client(glance_endpoint,
                                          token=self.auth_token)
        self.logger.info('glance connected')

    def connect_nova(self):
        self.nova = novaclient.Client(auth_url=self.auth_url,
                                      username=self.username,
                                      api_key=self.password,
                                      project_id=self.tenant_name,
                                      region_name=self.region_name)
        self.logger.info('nova connected')

    def connect_neutron(self):
        self.neutron = neutronclient.Client(auth_url=self.auth_url,
                                            username=self.username,
                                            password=self.password,
                                            tenant_name=self.tenant_name,
                                            region_name=self.region_name)
        self.logger.info('neutron connected')

    def connect_cinder(self):
        self.cinder = cinderclient.Client(auth_url=self.auth_url,
                                          username=self.username,
                                          api_key=self.password,
                                          project_id=self.tenant_name,
                                          region_name=self.region_name)
        self.logger.info('cinder connected')

    def connect_heat(self):
        heat_endpoint = self.keystone.service_catalog.url_for(
            service_type='orchestration')
        self.heat = heatclient.Client(heat_endpoint, token=self.auth_token)
        self.logger.info('heat connected')

    def connect_ceilometer(self):
        ceilometer_endpoint = self.keystone.service_catalog.url_for(
            service_type='metering')
        self.ceilometer = ceilometerclient.Client(ceilometer_endpoint,
                                                  token=self.auth_token)
        self.logger.info('ceilometer connected')

    def print_info(self):
        print 'Connection to instance {} working! You have {} image(s), ' \
              '{} virtual machine(s), {} network(s) and {} router(s).'.format(
                  self.name,
                  len(list(self.glance.images.list())),
                  len(self.nova.servers.list()),
                  len(self.neutron.list_networks()),
                  len(self.neutron.list_routers()))
