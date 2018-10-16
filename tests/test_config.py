from ldap3 import ALL, Connection, Server
import logging
import yaml
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

config_file = Path(__file__).absolute().parent / "test-config.yaml"
with config_file.open() as fh:
    config = yaml.load(fh)


def connect3(host, user, password):
    s = Server(host, use_ssl=False, get_info=ALL)
    c = Connection(s, user=user, password=password)
    log.debug("Binding")
    if not c.bind():
        raise Exception(c.result)
    log.debug("Bound")
    return c


def connect():
    return connect3(**config["test"])


import logging

import connexion
from flask_testing import TestCase

from app import DataclassEncoder


class BaseTestCase(TestCase):
    def create_app(self):
        logging.getLogger("connexion.operation").setLevel("ERROR")
        app = connexion.App(__name__, specification_dir="..")
        app.app.json_encoder = DataclassEncoder
        app.app.config.update(config)
        app.add_api("openapi.yaml")
        return app.app
