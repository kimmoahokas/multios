__author__ = 'Kimmo Ahokas'


from flask.ext.restful import Resource

from multios.server import app


class OpenStackList(Resource):
    def get(self):
        app.logger.debug('OpenStackList.get() called')
        return 'Should list configured OpenStacks'


class OpenStack(Resource):
    def get(self, os_id):
        app.logger.debug('OpenStack.get() called')
        return 'Should return information on specified OpenStack instance ' \
               '{}'.format(os_id)
