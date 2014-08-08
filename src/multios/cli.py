from __future__ import print_function

import sys
import logging
import docopt
from multios.base.configparser import load_config_file
from multios.base import exceptions

logger = logging.getLogger('multios.cli')


class MultiOSCLI(object):
    """MultiOS CLI
    MultiOS is a tool for working with multiple independent OpenStack installations.

    Usage:
        multios [options] info

    Options:
        -h --help   Show this help message and exit.
        -l (CRITICAL | ERROR | WARNING | INFO | DEBUG)  set logging level [default: WARNING].
        -c <config_file>  use specified config file [default: config.json].
    """

    def __init__(self, argv=None):
        """

        :param argv: Array of command line arguments.
        :return:
        """
        if argv is None:
            argv=sys.argv[1:]
        self.argv = argv
        self.parsed_arguments = None
        self.logger = None
        self.config = None

    def main(self):
        self.parse_command_line()
        self.configure_logging()
        try:
            self.read_config_file()
            self.start_cli()
            return 0
        except exceptions.MultiOSError as e:
            print('Error: {}'.format(e), file=sys.stderr)
            return 1

    def parse_command_line(self):
        self.parsed_arguments = docopt.docopt(self.__doc__, self.argv)

    def configure_logging(self):
        log_level = self.get_log_level()
        root_logger = logging.getLogger('multios')
        root_logger.setLevel(log_level)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(levelname)s:%(name)s: %(message)s')
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

    def read_config_file(self):
        self.config = load_config_file(self.parsed_arguments['-c'])
        if self.config is None:
            raise exceptions.ConfigFileError('No config returned.')

    def start_cli(self):
        if self.parsed_arguments['info']:
            self.print_info()

    def print_info(self):
        print('CLI configured with {} OpenStack instance(s)'.format(len(
            self.config['instances'])))
        for instance in self.config['instances']:
            print(instance)


def main():
    try:
        value = MultiOSCLI().main()
        exit(value)
    except KeyboardInterrupt:
        print('Stopping MultiOS cli...')
        sys.exit(130)
    except Exception as e:
        # Catch errors that somehow slipped past all previous checks
        logger.debug(e, exc_info=True)
        print('ERROR: {}'.format(e), file=sys.stderr)
        exit(1)