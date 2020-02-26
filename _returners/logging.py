# -*- coding: utf-8 -*-
'''
Return data to a remote syslog facility
To use the logging returner, append '--return logging' to the
salt command.
.. code-block:: bash
    salt '*' test.ping --return logging
The following fields can be set in the minion conf file::
    logging.level (optional, Default: INFO)
    logging.facility (optional, Default: LOG_USER)
    logging.remote_port (optional, Default: 514)
    logging.remote_ip (optional, Default: '127.0.0.1')
    logging.logger_name (optional, Default: 'Salt-Master')
'''
from __future__ import absolute_import, print_function, unicode_literals

# Import python libs
try:
    import logging
    import logging.handlers
    HAS_LOGGING = True
except ImportError:
    HAS_LOGGING = False

# Import Salt libs
import salt.utils.jid
import salt.utils.json
import salt.returners
from salt.ext import six

log = logging.getLogger(__name__)
# Define the module's virtual name
__virtualname__ = 'logging'


def _get_options(ret=None):
    '''
    Get the returner options from salt.
    '''

    defaults = {'level': 'INFO',
                'facility': 'LOG_USER',
                'remote_port': 514,
                'remote_ip': '127.0.0.1',
                'logger_name': 'Salt-Master'
                }

    attrs = {'level': 'level',
             'facility': 'facility',
             'remote_ip': 'remote_ip',
             'remote_port': 'remote_port',
             'logger_name': 'logger_name'
             }

    _options = salt.returners.get_returner_options(__virtualname__,
                                                   ret,
                                                   attrs,
                                                   __salt__=__salt__,
                                                   __opts__=__opts__,
                                                   defaults=defaults)
    return _options


def _verify_options(options):
    '''
    Verify options and log warnings
    Returns True if all options can be verified,
    otherwise False
    '''

    # Sanity check port
    if 'port' in options:
        if not isinstance(options['port'], int):
            log.error('port must be an int')
            return False

    # Sanity check tag
    if 'tag' in options:
        if not isinstance(options['tag'], six.string_types):
            log.error('tag must be a string')
            return False
        if len(options['tag']) > 32:
            log.error('tag size is limited to 32 characters')
            return False

    return True


def __virtual__():
    if not HAS_LOGGING:
        return False, 'Could not import logging returner; logging is not installed.'
    return __virtualname__


def returner(ret):
    '''
    Return data to the remote syslog
    '''
    _options = _get_options(ret)

    if not _verify_options(_options):
        return

    remote_ip = _options.get('remote_ip')
    remote_port = _options.get('remote_port')
    level = logging.getLevelName(_options.get('level'))

    my_logger = logging.getLogger(_options.get('logger_name'))
    my_logger.setLevel(level)

    handler = logging.handlers.SysLogHandler(address = (remote_ip, remote_port))

    my_logger.addHandler(handler)

    my_logger.log(level, salt.utils.json.dumps(ret))
    del my_logger

def prep_jid(nocache=False,
             passed_jid=None):  # pylint: disable=unused-argument
    '''
    Do any work necessary to prepare a JID, including sending a custom id
    '''
    return passed_jid if passed_jid is not None else salt.utils.jid.gen_jid(__opts__)

def save_load(jid, load, minions=None):
    '''
    Return data to the remote syslog
    '''

def get_load(jid):
  ret = {}
  return ret
