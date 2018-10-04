from app import connect3
from flask import current_app
from ipa.api_filter import parse_filter
from ipa.model import *


def get_amministrazione(codice_ipa, fields=None):
    attributes = parse_filter(fields) if fields else "*"

    c = connect3(**current_app.config["server"])
    c.search(
        search_base=f"o={codice_ipa},c=it",
        search_scope=0,
        attributes=attributes,
        size_limit=1,
        search_filter="(&(objectclass=amministrazione)(codiceFiscaleAmm=*))",
    )
    ret = []
    for entry in c.response:
        x = entry["attributes"]
        current_app.logger.debug("entry: %r", entry)
        try:
            a = Amministrazione.from_ldap(**x)
            current_app.logger.debug(a.yaml())
            ret.append(a)
        except:
            current_app.logger.warning("Errore processando ente: {}", x)
    return {"entries": ret}


def get_amministrazioni(limit=10, fields=None):

    attributes = parse_filter(fields) if fields else "*"

    c = connect3(**current_app.config["server"])
    c.search(
        search_base="c=it",
        search_scope=1,
        attributes=attributes,
        size_limit=limit,
        search_filter="(&(objectclass=amministrazione)(codiceFiscaleAmm=*))",
    )
    ret = []
    for entry in c.response:
        x = entry["attributes"]
        # print("=" * 40, x)
        try:
            a = Amministrazione.from_ldap(**x)
            current_app.logger.debug(a.yaml())
            ret.append(a)
        except:
            current_app.logger.warning("Errore processando ente: {}", x)
    return {"entries": ret}
