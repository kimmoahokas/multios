from __future__ import print_function

import sys
import logging

import docopt

from multios.base import exceptions

logger = logging.getLogger('multios.cli')
VERSION = '0.1alpha'


class MultiOSCLI(object):
    """MultiOS CLI
MultiOS is a tool for working with multiple independent OpenStack installations.

Usage:
    multios [options] info
    multios [options] boot [<name>]
    multios [options] stop <name>
    multios [options] server
    multios (-h | --help | --version)

Options:
    -h --help  Show this help message and exit.
    --version  Print software version and exit.
    -l (CRITICAL | ERROR | WARNING | INFO | DEBUG)  set logging level.
    """

    def __init__(self, argv=None):
        """

        :param argv: Array of command line arguments.
        :return:
        """
        if argv is None:
            argv = sys.argv[1:]
        self.argv = argv
        self.parsed_arguments = None
        self.logger = None

    def main(self):
        self.parse_command_line()
        self.configure_logging()
        try:
            self.run_command()
            return 0
        except exceptions.MultiOSError as e:
            if self.logger is not None:
                logger.exception("Unhandled exception", exc_info=e)
            else:
                print('Error: {}'.format(e), file=sys.stderr)
            return 1

    def parse_command_line(self):
        self.parsed_arguments = docopt.docopt(self.__doc__, self.argv,
                                              help=True, version=VERSION)

    def configure_logging(self):
        """ Setup the Python logging module. The same config is used by server.
        :return: None
        """
        log_level = self.get_log_level()

        root_logger = logging.getLogger('multios.cli')
        root_logger.setLevel(log_level)
        ch = logging.StreamHandler()
        ch.setLevel(log_level)
        formatter = logging.Formatter('%(levelname)s %(name)s: %(message)s')
        ch.setFormatter(formatter)
        root_logger.addHandler(ch)
        self.logger = logging.getLogger('multios.cli.MultiosCLI')
        self.logger.info('Logging configured with log level %s',
                         logging.getLevelName(log_level))

    def get_log_level(self):
        log_levels = {'CRITICAL': logging.CRITICAL, 'ERROR': logging.ERROR,
                      'WARNING': logging.WARNING, 'INFO': logging.INFO,
                      'DEBUG': logging.DEBUG}
        level_string = self.parsed_arguments['-l'].upper()
        log_level = log_levels[level_string] if level_string in log_levels \
            else logging.WARNING
        return log_level

    def run_command(self):
        if self.parsed_arguments['info']:
            self.print_info()
        elif self.parsed_arguments['boot']:
            self.boot_instance()
        elif self.parsed_arguments['stop']:
            self.stop_instance(self.parsed_arguments['name'])
        elif self.parsed_arguments['server']:
            self.start_server()
        else:
            print('No valid command found, stopping!')

    def print_info(self):
        """Print information about connected OpenStack instances."""
        print('Should print basic info. Not implemented.')

    def boot_instance(self):
        """Launch instance in one of the configured OpenStacks."""
        print('Should boot new instance. Not implemented.')

    def stop_instance(self, instance):
        """Stop specified instance."""
        print('Should stop specified instance. Not implemented.')

    def start_server(self):
        """Start Development Multios API server."""

        # Only import the Flask app when needed. This also makes Flask to use
        # the same logging configuration created by CLI.
        self.logger.debug('Importing multios.server from cli.start_server()')
        from multios.server import app
        app.run(host='0.0.0.0', use_reloader=False,
                debug=True, use_debugger=False)


def main(argv=None):
    try:
        value = MultiOSCLI(argv).main()
        exit(value)
    except KeyboardInterrupt:
        print('Stopping MultiOS cli...')
        sys.exit(130)
    except Exception as e:
        # Catch errors that somehow slipped past all previous checks
        logger.exception(e, exc_info=True)
        print('ERROR: {}'.format(e), file=sys.stderr)
        exit(1)