from dataclasses import asdict
from os.path import dirname
from os.path import join as pjoin

from app import connect3
from connexion import problem
from flask import current_app, request
from ipa.api_filter import parse_fields
from ipa.model import AOO, Amministrazione, Ufficio
from .util import assert_one_entry


def get_amministrazione(codice_ipa, fields=None):
    attributes = parse_fields(fields) if fields else "*"

    c = connect3(**current_app.config["server"])
    c.search(
        search_base=f"o={codice_ipa},c=it",
        search_scope=0,
        attributes=attributes,
        size_limit=1,
        search_filter="(&(objectclass=amministrazione)(codiceFiscaleAmm=*))",
    )
    ret = []

    assert_one_entry(c.result["result"])

    for entry in c.response:
        current_app.logger.debug("entry: %r", entry)
        x = entry["attributes"]
        try:
            a = Amministrazione.from_ldap(**x)
            a.links = {
                "self": request.url,
                "related": [
                    pjoin(request.url, "uffici"),
                    pjoin(request.url),
                    "aree_organizzative_omogenee",
                ],
            }
            current_app.logger.debug(a.yaml())

            ret.append(a)
        except (IndexError, KeyError, ValueError, TypeError):
            current_app.logger.exception("Errore processando ente: %r", x)
    if ret:
        return ret[0]
    return problem(
        status=500,
        title="Not Found",
        instance=request.url,
        detail="Entry found but not returned.",
    )


def list_amministrazioni(
    limit=10, fields=None, codice_ipa=None, mail=None, codice_fiscale=None
):

    attributes = parse_fields(fields) if fields else "*"

    search_filter = ""
    if codice_ipa:
        search_filter += f"(o={codice_ipa})"
    if codice_fiscale:
        search_filter += f"(codiceFiscaleAmm={codice_fiscale})"
    if mail:
        search_filter += (
            f"(|"
            f"(mail={mail})"
            f"(contatti={mail}*)"
            f"(mailS=*{mail})"
            f")"
        )

    c = connect3(**current_app.config["server"])
    current_app.logger.debug("Searching with %r", search_filter)
    c.search(
        search_base="c=it",
        search_scope=1,
        attributes=attributes,
        size_limit=limit,
        search_filter=f"(&(objectclass=amministrazione)"
        f"(codiceFiscaleAmm=*)"
        f"{search_filter})",
    )

    # Links
    for baseurl in current_app.blueprints.keys():
        self_fmt = f"{baseurl}" "/amministrazione/{codice_ipa}"
        uffici_fmt = f"{baseurl}" "/amministrazione/{codice_ipa}/uffici"
        aoo_fmt = (
            f"{baseurl}"
            "/amministrazione/{codice_ipa}/aree_organizzative_omogenee"
        )

    ret = []
    for entry in c.response:
        x = entry["attributes"]
        current_app.logger.debug("entry: %r", entry)
        try:
            a = Amministrazione.from_ldap(**x)
            a.links = {
                "self": self_fmt.format(**asdict(a)),
                "related": [
                    uffici_fmt.format(**asdict(a)),
                    aoo_fmt.format(**asdict(a)),
                ],
            }
            current_app.logger.debug(a.yaml())
            ret.append(a)
        except (IndexError, KeyError, ValueError, TypeError):
            current_app.logger.exception("Errore processando ente: %r", x)
    return {"items": ret, "count": len(ret), "limit": limit}
