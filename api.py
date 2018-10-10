from os.path import dirname
from os.path import join as pjoin

from app import connect3
from connexion import problem
from flask import current_app, request
from ipa.api_filter import parse_fields
from ipa.model import Amministrazione, Ufficio


def assert_one_entry(ldap_connection):
    if ldap_connection.result["result"] == 0:
        return problem(
            status=404,
            title="Not Found",
            instance=request.url,
            detail="Ufficio not found",
        )
    if ldap_connection.result["result"] > 1:
        return problem(
            status=404,
            title="Not Found",
            instance=request.url,
            detail="More than one entry",
        )


def link_from_entry(**kwargs):
    assert "objectclass" in kwargs
    if "aoo" in kwargs["objectclass"]:
        raise NotImplementedError
    if "ufficio" in kwargs["objectclass"]:
        raise NotImplementedError
    if "amministrazionie" in kwargs["objectclass"]:
        raise NotImplementedError
    raise NotImplementedError


def status():
    """
    Connect and disconnect from the LDAP Server. If it works, return 200.
    :return:
    """
    c = connect3(**current_app.config["server"])
    c.unbind()
    return problem(
        status=200,
        title="Success",
        detail="Application is working normally",
        ext={"result": "ok"},
    )


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

    assert_one_entry(c)

    for entry in c.response:
        x = entry["attributes"]
        current_app.logger.debug("entry: %r", entry)
        try:
            a = Amministrazione.from_ldap(**x)
            current_app.logger.debug(a.yaml())

            ret.append(a)
        except (IndexError, KeyError, ValueError, TypeError):
            current_app.logger.warning("Errore processando ente: %r", x)
    if ret:
        return {"items": ret}
    return problem(
        status=500,
        title="Not Found",
        instance=request.url,
        detail="Entry found but not returned.",
    )


def get_amministrazioni(
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
    ret = []
    for entry in c.response:
        x = entry["attributes"]
        current_app.logger.debug("entry: %r", entry)
        try:
            a = Amministrazione.from_ldap(**x)
            a.links = {
                "self": pjoin(
                    dirname(request.url), "amministrazione", a.codice_ipa
                )
            }
            current_app.logger.debug(a.yaml())
            ret.append(a)
        except (IndexError, KeyError, ValueError, TypeError):
            current_app.logger.warning("Errore processando ente: %r", x)
    return {"items": ret, "count": len(ret)}


def get_uffici(
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
    ret = []
    for entry in c.response:
        x = entry["attributes"]
        current_app.logger.debug("entry: %r", entry)
        try:
            a = Ufficio.from_ldap(**x)
            a.links = {
                "self": pjoin(
                    dirname(request.url), "ufficio", a.codice_univoco_ufficio
                )
            }
            current_app.logger.debug(a.yaml())
            ret.append(a)
        except (IndexError, KeyError, ValueError, TypeError) as e:
            current_app.logger.exception(
                "Errore processando ente: %r", x, exc_info=True
            )
            current_app.logger.debug(e)
    return {"items": ret, "coount": len(ret)}


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
        size_limit=2,
        search_filter=f"(&(objectclass=ufficio){search_filter})",
    )
    ret = []

    assert_one_entry(c)

    for entry in c.response:
        x = entry["attributes"]
        current_app.logger.debug("entry: %r", entry)
        try:
            a = Ufficio.from_ldap(**x)
            a.links = {
                "self": pjoin(dirname(request.url), a.codice_univoco_ufficio),
                "parent": pjoin(
                    dirname(dirname(request.url)),
                    "amministrazione",
                    a.codice_ipa,
                ),
            }
            current_app.logger.debug(a.yaml())
            ret.append(a)
        except (IndexError, KeyError, ValueError, TypeError):
            current_app.logger.exception("Errore processando ente: %r", x)
    if ret:
        return {"items": ret}
    return problem(
        status=500,
        title="Not Found",
        instance=request.url,
        detail="Entry found but not returned.",
    )


#
# Aliases.
#
get_uffici_by_ipa = get_uffici
get_ufficio_by_ipa = get_ufficio
