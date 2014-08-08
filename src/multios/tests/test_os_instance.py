import unittest
import mock

from multios.base.os_instance import OpenStackInstance

__author__ = 'Kimmo Ahokas'


class TestOpenStackInstance(unittest.TestCase):
    def setUp(self):
        self.access_token = 'aToken'
        self.config = {'name': 'TestInstance',
                       'auth_url': 'http://example.com:5000/v2.0',
                       'username': 'TestUser',
                       'password': 'TestPassword',
                       'tenant_name': 'TestTenant',
                       'region_name': 'regionOne'}

        self.catalog = {'metering': 'http://example.com:8777',
                        'volume': 'http://example.com:8776/v1/%(tenant_id)s',
                        'volumev2': 'http://example.com:8776/v2/%(tenant_id)s',
                        'image': 'http://example.com:9292',
                        'compute': 'http://example.com:8774/v2/%(tenant_id)s',
                        'network': 'http://example.com:9696',
                        'identity': 'http://example.com:5000/v2.0',
                        'orchestration': 'http://example.com:8004/v1/%(tenant_id)s',
                        'cloudformation': 'http://example.com:8000/v1'}

        def url_for(service_type):
            if service_type in self.catalog:
                return self.catalog[service_type]
            raise Exception('Invalid service type')

        self.keystone_patcher = mock.patch('keystoneclient.v2_0.client.Client',
                                           autospec=True)
        self.glance_patcher = mock.patch('glanceclient.v2.client.Client',
                                         autospec=True)
        self.nova_patcher = mock.patch('novaclient.v1_1.client.Client',
                                       autospec=True)
        self.neutron_patcher = mock.patch('neutronclient.v2_0.client.Client',
                                          autospec=True)
        self.cinder_patcher = mock.patch('cinderclient.v2.client.Client',
                                         autospec=True)
        self.heat_patcher = mock.patch('heatclient.v1.client.Client',
                                       autospec=True)
        self.ceilometer_patcher = mock.patch(
            'ceilometerclient.v2.client.Client', autospec=True)

        self.keystone_mock = self.keystone_patcher.start()
        self.keystone_mock.return_value.service_catalog.url_for.side_effect = \
            url_for
        self.keystone_mock.return_value.auth_token = self.access_token
        self.glance_mock = self.glance_patcher.start()
        self.nova_mock = self.nova_patcher.start()
        self.neutron_mock = self.neutron_patcher.start()
        self.cinder_mock = self.cinder_patcher.start()
        self.heat_mock = self.heat_patcher.start()
        self.ceilometer_mock = self.ceilometer_patcher.start()

        self.instance = OpenStackInstance(self.config['name'],
                                          self.config['auth_url'],
                                          self.config['username'],
                                          self.config['password'],
                                          self.config['tenant_name'],
                                          self.config['region_name'],
                                          True)

    def tearDown(self):
        self.keystone_patcher.stop()
        # self.auth_token_patcher.stop()
        self.glance_patcher.stop()
        self.nova_patcher.stop()
        self.neutron_patcher.stop()
        self.cinder_patcher.stop()
        self.heat_patcher.stop()
        self.ceilometer_patcher.stop()

    @mock.patch('multios.base.os_instance.OpenStackInstance.__init__')
    def test_create_from_config(self, init_mock):
        init_mock.return_value = None
        OpenStackInstance.create_from_config(self.config)
        init_mock.assert_called_once_with(self.config['name'],
                                          self.config['auth_url'],
                                          self.config['username'],
                                          self.config['password'],
                                          self.config['tenant_name'],
                                          self.config['region_name'],
                                          True)

    @mock.patch('multios.base.os_instance.OpenStackInstance._connect_keystone')
    @mock.patch('multios.base.os_instance.OpenStackInstance'
                '._connect_all_optional_services')
    def test_init(self, connect_optional_services_mock, connect_keystone_mock):
        OpenStackInstance(self.config['name'],
                          self.config['auth_url'],
                          self.config['username'],
                          self.config['password'],
                          self.config['tenant_name'],
                          self.config['region_name'],
                          True)
        connect_keystone_mock.assert_called_once_with()
        self.assertFalse(connect_optional_services_mock.called,
                         "Optional services were connected during init while "
                         "lazy_load was set to true")

        connect_keystone_mock.reset_mock()
        connect_optional_services_mock.reset_mock()

        OpenStackInstance(self.config['name'],
                          self.config['auth_url'],
                          self.config['username'],
                          self.config['password'],
                          self.config['tenant_name'],
                          self.config['region_name'],
                          False)
        connect_keystone_mock.assert_called_once_with()
        connect_optional_services_mock.assert_called_once_with()

    def test_connect_all_optional_services(self):
        # this test mainly relies on other tests
        self.assertIsNone(self.instance._glance)
        self.assertIsNone(self.instance._nova)
        self.assertIsNone(self.instance._neutron)
        self.assertIsNone(self.instance._cinder)
        self.assertIsNone(self.instance._heat)
        self.assertIsNone(self.instance._ceilometer)
        self.instance._connect_all_optional_services()
        self.assertIsNotNone(self.instance._glance)
        self.assertIsNotNone(self.instance._nova)
        self.assertIsNotNone(self.instance._neutron)
        self.assertIsNotNone(self.instance._cinder)
        self.assertIsNotNone(self.instance._heat)
        self.assertIsNotNone(self.instance._ceilometer)

    def test_connect_keystone(self):
        self.assertIsNotNone(self.instance._keystone)
        self.assertEqual(self.instance.keystone,
                         self.keystone_mock.return_value)
        self.keystone_mock.assert_called_once_with(
            auth_url=self.config['auth_url'],
            username=self.config['username'],
            password=self.config['password'],
            tenant_name=self.config['tenant_name'],
            region_name=self.config['region_name'])
        #self.assertEqual(self.instance.auth_token, self.access_token)

    def test_connect_glance(self):
        self.assertIsNone(self.instance._glance)
        self.instance._connect_glance()
        self.keystone_mock.return_value.service_catalog.url_for \
            .assert_called_once_with(service_type='image')
        self.assertEqual(self.instance.glance, self.glance_mock.return_value)
        self.glance_mock.assert_called_once_with(self.catalog['image'],
                                                 token=self.access_token)

    def test_connect_nova(self):
        self.assertIsNone(self.instance._nova)
        self.instance._connect_nova()
        self.assertEqual(self.instance.nova, self.nova_mock.return_value)
        self.nova_mock.assert_called_once_with(
            auth_url=self.config['auth_url'],
            username=self.config['username'],
            api_key=self.config['password'],
            project_id=self.config['tenant_name'],
            region_name=self.config['region_name'])

    def test_connect_neutron(self):
        self.assertIsNone(self.instance._neutron)
        self.instance._connect_neutron()
        self.assertEqual(self.instance.neutron, self.neutron_mock.return_value)
        self.neutron_mock.assert_called_once_with(
            auth_url=self.config['auth_url'],
            username=self.config['username'],
            password=self.config['password'],
            tenant_name=self.config['tenant_name'],
            region_name=self.config['region_name'])

    def test_connect_cinder(self):
        self.assertIsNone(self.instance._cinder)
        self.instance._connect_cinder()
        self.assertEqual(self.instance.cinder, self.cinder_mock.return_value)
        self.cinder_mock.assert_called_once_with(
            auth_url=self.config['auth_url'],
            username=self.config['username'],
            api_key=self.config['password'],
            project_id=self.config['tenant_name'],
            region_name=self.config['region_name'])

    def test_connect_heat(self):
        self.assertIsNone(self.instance._heat)
        self.instance._connect_heat()
        self.assertEqual(self.instance.heat, self.heat_mock.return_value)
        self.keystone_mock.return_value.service_catalog.url_for \
            .assert_called_once_with(service_type='orchestration')
        self.heat_mock.assert_called_once_with(self.catalog['orchestration'],
                                               token=self.access_token)

    @unittest.expectedFailure
    def test_connect_ceilometer(self):
        self.assertIsNone(self.instance._ceilometer)
        self.instance._connect_ceilometer()
        self.assertEqual(self.instance.ceilometer,
                         self.ceilometer_mock.return_value)
        self.keystone_mock.return_value.service_catalog.url_for \
            .assert_called_once_with(service_type='metering')
        # TODO: how to check that the mock was called with certain lambda?
        self.ceilometer_mock.assert_called_once_with(self.catalog['metering'],
                                                     token=self.access_token)
