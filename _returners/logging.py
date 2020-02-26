# -*- coding: utf-8 -*-
'''
Return data to a remote syslog facility
To use the logging returner, append '--return logging' to the
salt command.
.. code-block:: bash
    salt '*' test.ping --return logging
The following fields can be set in the minion conf file::
    logging.level (optional, Default: LOG_INFO)
    logging.facility (optional, Default: LOG_USER)
    logging.tag (optional, Default: salt-minion)
    logging.options (list, optional, Default: [])
Available levels, facilities, and options can be found in the
``syslog`` docs for your python version.
.. note::
    The default tag comes from ``sys.argv[0]`` which is
    usually "salt-minion" but could be different based on
    the specific environment.
Configuration example:
.. code-block:: yaml
    syslog.level: 'LOG_ERR'
    syslog.facility: 'LOG_DAEMON'
    syslog.tag: 'mysalt'
    syslog.options:
      - LOG_PID
Of course you can also nest the options:
.. code-block:: yaml
    syslog:
      level: 'LOG_ERR'
      facility: 'LOG_DAEMON'
      tag: 'mysalt'
      options:
        - LOG_PID
Alternative configuration values can be used by
prefacing the configuration. Any values not found
in the alternative configuration will be pulled from
the default location:
.. code-block:: yaml
    alternative.syslog.level: 'LOG_WARN'
    alternative.syslog.facility: 'LOG_NEWS'
To use the alternative configuration, append
``--return_config alternative`` to the salt command.
.. versionadded:: 2015.5.0
.. code-block:: bash
    salt '*' test.ping --return syslog --return_config alternative
To override individual configuration items, append
--return_kwargs '{"key:": "value"}' to the salt command.
.. versionadded:: 2016.3.0
.. code-block:: bash
    salt '*' test.ping --return syslog --return_kwargs '{"level": "LOG_DEBUG"}'
.. note::
    Syslog server implementations may have limits on the maximum
    record size received by the client. This may lead to job
    return data being truncated in the syslog server's logs. For
    example, for rsyslog on RHEL-based systems, the default
    maximum record size is approximately 2KB (which return data
    can easily exceed). This is configurable in rsyslog.conf via
    the $MaxMessageSize config parameter. Please consult your syslog
    implmentation's documentation to determine how to adjust this limit.
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
                'options': []
                }

    attrs = {'level': 'level',
             'facility': 'facility',
             'tag': 'tag',
             'remote_ip': 'remote_ip',
             'remote_port': 'remote_port',
             'options': 'options'
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
            log.error('tag must be a string')
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

    my_logger = logging.getLogger('Salt-Master')
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
