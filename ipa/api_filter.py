#
# API filter to LDAP Filter
#
from ipa.model import Amministrazione, Location, Responsabile, Servizio


def parse_filter(q_filter):
    mappa_attributi = Amministrazione.q_fields()
    items = list(q_filter.split(","))
    ret = []
    if "location" in items:
        items.remove("location")
        ret += [ldap_f for api_f, ldap_f in Location.q_fields().items()]

    if "responsabile" in items:
        items.remove("responsabile")
        ret += [ldap_f for api_f, ldap_f in Responsabile.q_fields().items()]

    if "servizi" in items:
        items.remove("servizi")
        ret += [ldap_f for api_f, ldap_f in Servizio.q_fields().items()]

    ret += [mappa_attributi[i] for i in items]
    return ret
