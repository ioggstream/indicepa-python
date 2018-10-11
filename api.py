from os.path import dirname
from os.path import join as pjoin

from app import connect3
from connexion import problem
from flask import current_app, request
from ipa.api_filter import parse_fields
from ipa.model import AOO, Amministrazione, Ufficio


def assert_one_entry(count):
    if count == 0:
        return problem(
            status=404,
            title="Not Found",
            instance=request.url,
            detail="Entry not found",
        )
    if count > 1:
        return problem(
            status=404,
            title="Not Found",
            instance=request.url,
            detail="More than one entry",
        )


def link_from_class(obj):
    ret = {"self": pjoin(dirname(request.url), obj.__class__.__name__, obj.id)}
    if isinstance(obj, Amministrazione):
        ret["related"] = [
            pjoin(ret["self"], "uffici"),
            pjoin(ret["self"], "aree_amministrative_omogenee"),
        ]
    if isinstance(obj, (Ufficio, AOO)):
        ret["parent"] = (
            pjoin(
                dirname(dirname(request.url)),
                "amministrazione",
                obj.codice_ipa,
            ),
        )
    return ret


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

    assert_one_entry(c.result["result"])

    for entry in c.response:
        current_app.logger.debug("entry: %r", entry)
        x = entry["attributes"]
        try:
            a = Amministrazione.from_ldap(**x)
            a.links = link_from_class(a)
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
            a.links = link_from_class(a)
            current_app.logger.debug(a.yaml())
            ret.append(a)
        except (IndexError, KeyError, ValueError, TypeError):
            current_app.logger.exception("Errore processando ente: %r", x)
    return {"items": ret, "count": len(ret), "limit": limit}


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
            u = Ufficio.from_ldap(**x)
            u.links = link_from_class(u)
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

    assert_one_entry(c.result["result"])

    for entry in c.response:
        x = entry["attributes"]
        current_app.logger.debug("entry: %r", entry)
        try:
            u = Ufficio.from_ldap(**x)
            u.links = link_from_class(u)
            current_app.logger.debug(u.yaml())
            ret.append(u)
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


def get_aoo(codice_ipa, codice_aoo, fields=None):
    items = list_aoo(
        codice_ipa=codice_ipa, codice_aoo=codice_aoo, fields=fields
    )
    assert_one_entry(len(items))
    return items["items"][0]


def list_aoo(codice_ipa, limit=10, fields=None, codice_aoo=None, **kwargs):

    search_base = "c=it"
    search_filter = ""
    attributes = parse_fields(fields, Ufficio) if fields else "*"
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
    ret = []
    for entry in c.response:
        current_app.logger.debug("entry: %r", entry)
        x = entry["attributes"]
        x["dn"] = entry["dn"]
        try:
            a = AOO.from_ldap(**x)
            a.links = {
                "self": pjoin(
                    dirname(request.url),
                    "area_organizzativa_omogenea",
                    a.codice_aoo,
                ),
                "parent": pjoin(
                    dirname(dirname(request.url)),
                    "amministrazione",
                    a.codice_ipa,
                ),
            }
            current_app.logger.debug(a.yaml())
            ret.append(a)
        except (IndexError, KeyError, ValueError, TypeError) as e:
            current_app.logger.exception(
                "Errore processando ente: %r", x, exc_info=True
            )
            current_app.logger.debug(e)
    return {"items": ret, "count": len(ret), "limit": limit}


#
# Aliases.
#
get_uffici_by_ipa = get_uffici
get_ufficio_by_ipa = get_ufficio
list_aoo_by_ipa = list_aoo
get_aoo_by_ipa = get_aoo
