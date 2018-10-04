import argparse
import json
from logging import basicConfig
from logging.config import dictConfig
from os.path import isfile

import connexion
import yaml
from flask import current_app as app
from flask.json import JSONEncoder
from ipa.model import JsonMixin
from ldap3 import ALL, Connection, Server  # TODO: use connection pool


def configure_logger(log_config="logging.yaml"):
    """Configure the logging subsystem."""
    if not isfile(log_config):
        return basicConfig()

    with open(log_config) as fh:
        log_config = yaml.load(fh)
        return dictConfig(log_config)


def connect3(host, user, password):
    s = Server(host, use_ssl=False, get_info=ALL)
    c = Connection(s, user=user, password=password)
    app.logger.debug("Binding")
    if not c.bind():
        raise Exception(c.result)
    app.logger.debug("Bound")
    return c


class DataclassEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, JsonMixin):
            return json.loads(obj.json())
        return JSONEncoder.default(self, obj)


if __name__ == "__main__":
    configure_logger()
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--credential",
        dest="credential",
        required=False,
        help="Point to the IdP metadata URL",
        default=False,
    )
    args = parser.parse_args()

    zapp = connexion.FlaskApp(__name__, port=8443, specification_dir="./")
    with open("config.yaml") as fh:
        zapp.app.config.update(yaml.load(fh))

    zapp.app.json_encoder = DataclassEncoder
    zapp.add_api("openapi.yaml", arguments={"title": "Hello World Example"})
    zapp.run(host="0.0.0.0", debug=True, ssl_context="adhoc")
