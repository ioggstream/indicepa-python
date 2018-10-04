from ldap3 import ALL, Connection, Server
import logging
import yaml
from pathlib import Path
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()


def connect3(host, user, password):
    s = Server(host, use_ssl=False, get_info=ALL)
    c = Connection(s, user=user, password=password)
    log.debug("Binding")
    if not c.bind():
        raise Exception(c.result)
    log.debug("Bound")
    return c


def connect():
    config_file = Path(__file__).absolute().parent / "test-config.yaml"
    with config_file.open() as fh:
        config = yaml.load(fh)
    return connect3(**config['test'])
