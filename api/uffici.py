from dataclasses import asdict
from os.path import dirname
from os.path import join as pjoin

from app import connect3
from connexion import problem
from flask import current_app, request
from ipa.api_filter import parse_fields
from ipa.model import Ufficio
from .util import assert_one_entry


def list_uffici(
    limit=10,
    fields=None,
    codice_ipa=None,
    codice_univoco_ufficio=None,
    **kwargs,
):

    search_base = "c=it"
    search_filter = ""
    attributes = parse_fields(fields, Ufficio) if fields else "*"
    mail = kwargs.get("mail")

    if codice_ipa:
        search_base = f"o={codice_ipa},c=it"
    if codice_univoco_ufficio:
        search_filter += f"(CodiceUnivocoUO={codice_univoco_ufficio})"
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
        search_filter=f"(&(objectclass=ufficio){search_filter})",
    )

    for baseurl in current_app.blueprints.keys():
        self_fmt = (
            f"{baseurl}"
            "/amministrazione/{codice_ipa}/ufficio/{codice_univoco_ufficio}"
        )
        parent_fmt = f"{baseurl}" "/amministrazione/{codice_ipa}"

    ret = []
    for entry in c.response:
        x = entry["attributes"]
        current_app.logger.debug("entry: %r", entry)
        try:
            u = Ufficio.from_ldap(**x)
            u.links = {
                "self": self_fmt.format(**asdict(u)),
                "parent": parent_fmt.format(**asdict(u)),
            }
            current_app.logger.debug(u.yaml())
            ret.append(u)
        except (IndexError, KeyError, ValueError, TypeError) as e:
            current_app.logger.exception(
                "Errore processando ente: %r", x, exc_info=True
            )
            current_app.logger.debug(e)
    return {"items": ret, "count": len(ret), "limit": limit}


def get_ufficio(
    codice_univoco_ufficio, codice_ipa=None, fields=None, **kwargs
):

    search_base = "c=it"
    search_filter = ""
    attributes = parse_fields(fields, cls=Ufficio) if fields else "*"
    mail = kwargs.get("mail")

    if codice_ipa:
        search_base = f"o={codice_ipa},c=it"
    if codice_univoco_ufficio:
        search_filter += f"(CodiceUnivocoUO={codice_univoco_ufficio})"
    if (
        mail
    ):  # XXX Troppe mail. Valutare separazione in fatturazione_elettronica.mail
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
        size_limit=2,
        search_filter=f"(&(objectclass=ufficio){search_filter})",
    )
    ret = []

    assert_one_entry(c.result["result"])

    for entry in c.response:
        x = entry["attributes"]
        current_app.logger.debug("entry: %r", entry)
        try:
            u = Ufficio.from_ldap(**x)
            u.links = {
                "self": request.url,
                "parent": dirname(dirname(request.url)),
            }
            current_app.logger.debug(u.yaml())
            ret.append(u)
        except (IndexError, KeyError, ValueError, TypeError):
            current_app.logger.exception("Errore processando ente: %r", entry)
    if ret:
        return ret[0]
    return problem(
        status=500,
        title="Not Found",
        instance=request.url,
        detail="Entry found but not returned.",
    )


#
# Aliases.
#
get_uffici_by_ipa = list_uffici
get_ufficio_by_ipa = get_ufficio
