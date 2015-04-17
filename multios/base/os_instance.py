from base.exceptions import MultiOSError

__author__ = 'Kimmo Ahokas'

import keystoneclient.v2_0.client as keystoneclient
import glanceclient.v2.client as glanceclient
import novaclient.v1_1.client as novaclient
import neutronclient.v2_0.client as neutronclient
import cinderclient.v2.client as cinderclient
import heatclient.v1.client as heatclient
import ceilometerclient.v2.client as ceilometerclient
from ceilometerclient import exc as ceilometer_exceptions
from keystoneclient import exceptions as keystone_exceptions
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

        :type self: OpenStackInstance
        """

        self.name = name
        self.auth_url = auth_url
        self.username = username
        self.password = password
        self.tenant_name = tenant_name
        self.region_name = region_name
        self.lazy_load = lazy_load

        self._keystone = None
        self._glance = None
        self._nova = None
        self._neutron = None
        self._cinder = None
        self._ceilometer = None
        self._heat = None

        self._keystone_connection_tried = False
        self._glance_connection_tried = False
        self._nova_connection_tried = False
        self._neutron_connection_tried = False
        self._cinder_connection_tried = False
        self._ceilometer_connection_tried = False
        self._heat_connection_tried = False

        self.logger = logging.getLogger('multios.base.{}.{}'.format(
            type(self).__name__,
            name))
        self._connect_keystone()

        if not self.lazy_load:
            self._connect_all_optional_services()

    @property
    def keystone(self):
        """

        :rtype : keystoneclient.Client
        """
        if self._keystone is None:
            self._connect_keystone()
        return self._keystone

    @property
    def glance(self):
        """

        :rtype : glanceclient.Client
        """
        if self._glance is None:
            self._connect_glance()
        return self._glance

    @property
    def nova(self):
        """

        :rtype : novaclient.Client
        """
        if self._nova is None:
            self._connect_nova()
        return self._nova

    @property
    def neutron(self):
        """

        :rtype : neutronclient.Client
        """
        if self._neutron is None:
            self._connect_neutron()
        return self._neutron

    @property
    def cinder(self):
        """

        :rtype : cinderclient.Client
        """
        if self._cinder is None:
            self._connect_cinder()
        return self._cinder

    @property
    def ceilometer(self):
        """

        :rtype : ceilometerclient.Client
        """
        if self._ceilometer is None:
            self._connect_ceilometer()
        return self._ceilometer

    @property
    def heat(self):
        """
        Get the Heat instance.

        :rtype: heatclient.Client
        """
        if self._heat is None:
            self._connect_heat()
        return self._heat

    def _connect_all_optional_services(self):
        self._connect_glance()
        self._connect_nova()
        self._connect_neutron()
        self._connect_cinder()
        self._connect_heat()
        self._connect_ceilometer()

    def _connect_keystone(self):
        if self._keystone_connection_tried:
            return
        self._keystone_connection_tried = True
        try:
            self._keystone = keystoneclient.Client(auth_url=self.auth_url,
                                                   username=self.username,
                                                   password=self.password,
                                                   tenant_name=self.tenant_name,
                                                   region_name=self.region_name)
            self.logger.info('keystone connected')
        except Exception as e:
            raise e

    def _connect_glance(self):
        if self._glance_connection_tried:
            return
        self._glance_connection_tried = True
        glance_endpoint = self._keystone.service_catalog.url_for(
            service_type='image')
        self._glance = glanceclient.Client(glance_endpoint,
                                           token=self._keystone.auth_token)
        self.logger.info('glance connected')

    def _connect_nova(self):
        if self._nova_connection_tried:
            return
        self._nova_connection_tried = True
        self._nova = novaclient.Client(auth_url=self.auth_url,
                                       username=self.username,
                                       api_key=self.password,
                                       project_id=self.tenant_name,
                                       region_name=self.region_name)
        self._nova.authenticate()
        self.logger.info('nova connected')

    def _connect_neutron(self):
        if self._neutron_connection_tried:
            return
        self._neutron_connection_tried = True
        self._neutron = neutronclient.Client(auth_url=self.auth_url,
                                             username=self.username,
                                             password=self.password,
                                             tenant_name=self.tenant_name,
                                             region_name=self.region_name)
        self.logger.info('neutron connected')

    def _connect_cinder(self):
        if self._cinder_connection_tried:
            return
        self._cinder_connection_tried = True
        try:
            self._cinder = cinderclient.Client(auth_url=self.auth_url,
                                               username=self.username,
                                               api_key=self.password,
                                               project_id=self.tenant_name,
                                               region_name=self.region_name)
            self._cinder.authenticate()
            self.logger.info('cinder connected')
        except keystone_exceptions.EndpointNotFound as e:
            self._cinder = None
            self.logger.warn(e)

    def _connect_heat(self):
        if self._heat_connection_tried:
            return
        self._heat_connection_tried = True
        try:
            heat_endpoint = self._keystone.service_catalog.url_for(
                service_type='orchestration')
            self._heat = heatclient.Client(heat_endpoint,
                                           token=self._keystone.auth_token)
            self.logger.info('heat connected')
        except keystone_exceptions.EndpointNotFound as e:
            self._heat = None
            self.logger.warn(e)

    def _connect_ceilometer(self):
        if self._ceilometer_connection_tried:
            return
        self._ceilometer_connection_tried = True
        try:
            ceilometer_endpoint = self._keystone.service_catalog.url_for(
                service_type='metering')
            # ceilometer client wants the auth token as callable object to
            # allow refreshing it so we pass a lambda
            self._ceilometer = ceilometerclient.Client(
                ceilometer_endpoint,
                token=lambda: self._keystone.auth_token)
            self.logger.info('ceilometer connected')
        except keystone_exceptions.EndpointNotFound as e:
            self._ceilometer = None
            self.logger.warn(e)

    def get_keystone_info(self):
        if self._keystone is not None:
            return 'Connected to {}'.format(self.auth_url)
        else:
            return 'Not connected'

    def get_glance_info(self):
        try:
            if self.glance is not None:
                image_list = list(self.glance.images.list())
                self.logger.debug('glance_info: {}'.format(image_list))
                return '{} image(s) available'.format(len(image_list))
            else:
                return 'Not connected'
        except Exception as e:
            self.logger.debug(e, exc_info=True)
            return 'Error!'

    def get_nova_info(self):
        if self.nova is not None:
            compute_list = self.nova.servers.list()
            self.logger.debug('nova info: {}'.format(compute_list))
            return '{} running instance(s)'.format(len(compute_list))
        else:
            return 'Not connected'

    def get_neutron_info(self):
        if self.neutron is not None:
            net_list = self.neutron.list_networks()['networks']
            router_list = self.neutron.list_routers()['routers']
            self.logger.debug('net info: {}'.format(net_list))
            self.logger.debug('router info: {}'.format(router_list))
            return '{} networks(s) and {} router(s)'.format(len(net_list),
                                                            len(router_list))
        else:
            return 'Not connected'

    def get_cinder_info(self):
        if self.cinder is not None:
            volume_list = self.cinder.volumes.list()
            self.logger.debug('cinder info: {}'.format(volume_list))
            return '{} volume(s)'.format(len(volume_list))
        else:
            return 'Not connected'

    def get_ceilometer_info(self):
        if self.ceilometer is not None:
            try:
                meters = self.ceilometer.meters.list()
                alarms = self.ceilometer.alarms.list()
                self.logger.debug('ceilometer meters: {}'.format(meters))
                self.logger.debug('ceilometer alarms: {}'.format(alarms))
                return '{} meter(s) and {} alarm(s)'.format(len(meters),
                                                            len(alarms))
            except ceilometer_exceptions.CommunicationError as e:
                self.logger.exception('Communication error while '
                                      'contacting Ceilometer', exc_info=e)
                return "Failed communication with Ceilometer: {}".format(
                    e.message)
        else:
            return 'Not connected'

    def get_heat_info(self):
        if self.heat is not None:
            return 'Not implemented'
        else:
            return 'Not connected'

    def _find_network_by_name(self, net_name):
        # TODO: fix this. network is not found
        net_id = self.neutron.show_network(net_name)
        return net_id

    def _find_image_by_name(self, image_name):
        image_list = list(self.glance.images.list(filters={'name': image_name}))
        if len(image_list) is not 1:
            raise MultiOSError('No such image "{}"'.format(image_name))
        return image_list[0]

    def launch_instance(self, params):
        name = params['name']
        image = self._find_image_by_name(params['image'])
        flavor = params['flavor']
        security_groups = params['security_groups']
        key_name = params['key_name']
        nics = []
        for network in params['networks']:
            nics.append({'net_id': self._find_network_by_name(network)})

        self.nova.servers.create(name, image, flavor,
                                 security_goups=security_groups,
                                 key_name=key_name,
                                 nics=nics)

    def stop_instance(self, instance):
        pass

    def create_network(self):
        pass

    def __str__(self):
        data = {'name': self.name,
                'keystone': self.get_keystone_info(),
                'glance': self.get_glance_info(),
                'nova': self.get_nova_info(),
                'neutron': self.get_neutron_info(),
                'cinder': self.get_cinder_info(),
                'ceilometer': self.get_ceilometer_info(),
                'heat': self.get_heat_info()}
        return 'OpenStack instance \'{name}\' with services:\n' \
               '  Keystone: {keystone}\n' \
               '  Glance: {glance}\n' \
               '  Nova: {nova}\n' \
               '  Neutron: {neutron}\n' \
               '  Cinder: {cinder}\n' \
               '  Ceilometer: {ceilometer}\n' \
               '  Heat: {heat}'.format(**data)
