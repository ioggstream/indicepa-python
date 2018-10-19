import argparse
import json
from logging import basicConfig
from logging.config import dictConfig
from os.path import isfile
from urllib.parse import urlparse

import connexion
import yaml
from connexion import ProblemException
from flask import current_app as app
from flask.json import JSONEncoder
from ipa.model import JsonMixin
from ldap3 import ALL, Connection, Server  # TODO: use connection pool
from ldap3.utils.log import EXTENDED, NETWORK, set_library_log_detail_level

set_library_log_detail_level(NETWORK)


def configure_logger(log_config="logging.yaml"):
    """Configure the logging subsystem."""
    if not isfile(log_config):
        return basicConfig()
    set_library_log_detail_level(NETWORK)

    return
    with open(log_config) as fh:
        log_config = yaml.load(fh)
        return dictConfig(log_config)


def connect3(host, user, password):
    s = Server(host, use_ssl=False, get_info=ALL)
    c = Connection(s, user=user, password=password)
    set_library_log_detail_level(EXTENDED)

    app.logger.debug("Binding")
    if not c.bind():
        raise ProblemException(
            detail=c.result, title="Internal Server Error", status=500
        )
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
        "--config",
        dest="config",
        required=False,
        help="The config file containing LDAP credentials.",
        default="config.yaml",
    )
    args = parser.parse_args()

    zapp = connexion.FlaskApp(__name__, port=8443, specification_dir="./")
    with open(args.config) as fh:
        zapp.app.config.update(yaml.load(fh))

    zapp.app.json_encoder = DataclassEncoder
    fapi = zapp.add_api(
        "openapi.yaml", arguments={"title": "Unofficial iPA convergent API"}
    )

    # Override openapi.yaml servers[0] netloc
    #  to expose WebUI on a public address.
    public_server = zapp.app.config.get("public_server")
    if public_server:
        server_one = fapi.__dict__["raw_spec"]["servers"][0]
        server_one["url"] = (
            urlparse(server_one["url"])
            ._replace(netloc=args.external_server)
            .geturl()
        )

    zapp.run(host="0.0.0.0", debug=True, ssl_context="adhoc")
