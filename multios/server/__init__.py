from __future__ import print_function
import sys

import os
from flask import Flask
from flask.ext import restful


def _load_config():
    """Load Flask configuration from multiple locations.
    :param app: Flask app to be configured
    :return: None
    """
    user_config = False
    # Read default configuration. The package is broken if this does not work
    app.config.from_object('multios.server.default_config')

    # Try to read user configuration from default location
    try:
        app.config.from_pyfile(app.config['CONFIG_FILE'], silent=False)
        user_config = True
        app.logger.info('Loaded config from file %s',
                        app.config['CONFIG_FILE'])
    except IOError as e:
        app.logger.info('Could not read config file %s',
                        app.config['CONFIG_FILE'])

    # Try to read user config from file specified in environment variable
    try:
        app.config.from_envvar(app.config['CONFIG_ENVVAR'], silent=False)
        user_config = True
        app.logger.info('Loaded config from file %s',
                        os.environ.get(app.config['CONFIG_ENVVAR']))
    except RuntimeError:
        app.logger.info('Environment variable %s was not set',
                        app.config['CONFIG_ENVVAR'])
    except IOError:
        app.logger.info('Could not read config file %s',
                        os.environ.get(app.config['CONFIG_ENVVAR']))

    # User-specific config was not found so the app can't function properly
    if not user_config:
        app.logger.critical('Could not load user-specific configuration, '
                            'exiting.')
        print('ERROR: Could not load user-specific configuration',
              file=sys.stderr)
        sys.exit(1)
    else:
        app.logger.info('Successfully loaded user configuration')

# Init the Flask app
# Note that this is done when ANY component from multios.server is IMPORTED!
app = Flask(__name__)
app.debug_log_format = '%(levelname)s %(name)s: %(message)s'
app.logger.debug('Created Flask APP with name "%s"', app.name)
_load_config()

# TODO: figure out way to prevent circular import
from base.os_instance import OpenStackInstance
app.logger.info('Connecting to configured OpenStack instances')
os_instances = []
for instance in app.config['INSTANCES']:
    os_instances.append(OpenStackInstance.create_from_config(instance))
app.logger.info('OpenStack instances connected!')

app.logger.debug('Creating Flask-Restful API')
api = restful.Api(app)
app.logger.debug('Flask-Restful API created')

# All project specific files can be imported only after app and api have been
# created
from multios.server.resource_loader import load_resources
load_resources(app, api)
