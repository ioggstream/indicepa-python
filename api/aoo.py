from dataclasses import asdict
from os.path import dirname
from os.path import join as pjoin

from app import connect3
from connexion import problem
from flask import current_app, request
from ipa.model import AOO, Amministrazione, Ufficio
from .util import assert_one_entry
from ipa.api_filter import parse_fields


def get_aoo(codice_ipa, codice_aoo, fields=None):
    items = list_aoo(
        codice_ipa=codice_ipa, codice_aoo=codice_aoo, fields=fields
    )
    assert_one_entry(len(items))
    return items["items"][0]


def list_aoo(codice_ipa, limit=10, fields=None, codice_aoo=None, **kwargs):
    search_base = "c=it"
    search_filter = ""
    attributes = parse_fields(fields, AOO) if fields else "*"
    mail = kwargs.get("mail")

    if codice_ipa:
        search_base = f"o={codice_ipa},c=it"
    if codice_aoo:
        search_filter += f"(aoo={codice_aoo})"
    if mail:
        search_filter += (
            f"(|"
            f"(mailResp={mail})"
            f"(mailRespSFE={mail}*)"
            f"(mailSFE=*{mail})"
            f")"
        )

    c = connect3(**current_app.config["server"])
    current_app.logger.debug("Searching with %r", search_filter)
    c.search(
        search_base=search_base,
        search_scope=2,
        attributes=attributes,
        size_limit=limit,
        search_filter=f"(&(objectclass=aoo){search_filter})",
    )
    for baseurl in current_app.blueprints.keys():
        self_fmt = (
            f"{baseurl}"
            "/amministrazione/{codice_ipa}/area_organizzativa_omogenea/{codice_aoo}"
        )
        parent_fmt = f"{baseurl}" "/amministrazione/{codice_ipa}"

    ret = []
    for entry in c.response:
        current_app.logger.debug("entry: %r", entry)
        try:
            x = entry["attributes"]
            x["dn"] = entry["dn"]
            a = AOO.from_ldap(**x)
            a.links = {
                "self": self_fmt.format(**asdict(a)),
                "parent": parent_fmt.format(**asdict(a)),
            }
            current_app.logger.debug(a.yaml())
            ret.append(a)
        except (IndexError, KeyError, ValueError, TypeError) as e:
            current_app.logger.exception(
                "Errore processando ente: %r con entry %r", x, a.yaml()
            )
            current_app.logger.debug(e)
    return {"items": ret, "count": len(ret), "limit": limit}


#
# Aliases.
#
list_aoo_by_ipa = list_aoo
get_aoo_by_ipa = get_aoo
