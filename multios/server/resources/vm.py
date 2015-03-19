__author__ = 'Kimmo Ahokas'

from flask.ext.restful import Resource

from multios.server import app


class VM(Resource):
    def get(self):
        app.logger.debug('VM.get() called')
        return "ASDF"

    def post(self):
        pass

