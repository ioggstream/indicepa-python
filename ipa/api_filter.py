#
# API filter to LDAP Filter
#
from ipa.model import Amministrazione, Location, Responsabile, Servizio


def parse_fields(q_filter, cls=Amministrazione):
    mappa_attributi = cls.q_fields()
    items = list(q_filter.split(","))

    # Add compulsory attributes.
    ret = ['objectClass', 'o', 'description']

    if "location" in items:
        items.remove("location")
        ret += [ldap_f for api_f, ldap_f in Location.q_fields().items()]

    if "responsabile" in items:
        items.remove("responsabile")
        ret += [ldap_f for api_f, ldap_f in Responsabile.q_fields().items()]

    if "servizi" in items:
        items.remove("servizi")
        ret += [ldap_f for api_f, ldap_f in Servizio.q_fields().items()]

    # TODO fatturazione

    ret += [mappa_attributi[i] for i in items]
    return ret
