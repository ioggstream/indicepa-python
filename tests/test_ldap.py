import logging

import yaml
from nose.tools import *

from ipa.model import (
    AOO,
    Amministrazione,
    FatturazioneElettronica,
    Location,
    Responsabile,
    Servizio,
    Ufficio,
    is_empty,
)
from samples import AvvStudioA_c_e472, c_e472, ced_c_e472, uc_trento, umc_latina_m_inf
from test_config import connect

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()


"""
{'objectClass': ['top', 'organization', 'amministrazione'], 'o': ['c_a462'], 'tipoAmm': 'L6', 'logoAmm': 'c_a462.gif', 'description': ['Comune di Ascoli Piceno'], 'postalCode': ['63100'], 'l': ['Ascoli Piceno'], 'provincia': 'AP', 'regione': 'Marche', 
'nomeResp': 'Guido', 'cognomeResp': 'Castelli', 'titoloResp': 'Sindaco', 'sitoIstituzionale': 'www.comuneap.gov.it', 'st': ['ACCREDITATA'], 'dataVerifica': '2018-02-27', 'codiceFiscaleAmm': '00229010442', 
'codiceAmm': '125155102201', 'street': ['Piazza Arringo, 7'], 'macroTipoAmm': 'PA', 'mail': ['comune.ascolipiceno@actaliscertymail.it'],
 'contatti': ['protocollo@comune.ascolipiceno.it#altro', 'urp@comune.ascolipiceno.it#altro', 'ufficio.comunicazione@comune.ascolipiceno.it#altro'], 'nomeS': ["1#1Sportello Unico per l'edilizia"], 'fruibS': ['1#true'], 'mailSPub': ['1#s']}


{'objectClass': ['top', 'organization', 'amministrazione'], 'o': ['c_a520'], 'tipoAmm': 'L6', 'dominioPEC': '@pec.comune.avio.tn.it', 'description': ['Comune di Avio'], 'postalCode': ['38063'], 'l': ['Avio'], 'provincia': 'TN', 'regione': 'Trentino Alto Adige', 'nomeResp': 'Federico', 'cognomeResp': 'Secchi', 'titoloResp': 'Sindaco', 'sitoIstituzionale': 'www.comune.avio.tn.it', 'st': ['ACCREDITATA'], 'dataVerifica': '2015-05-25', 'codiceFiscaleAmm': '00110390226', 'codiceAmm': '022007', 'street': ['Piazza Vittorio Emanuele III, 1'], 'macroTipoAmm': 'PA', 'mail': ['segreteria@pec.comune.avio.tn.it'], 'contatti': ['segreteria@comune.avio.tn.it#altro'], 'nomeS': ['1#Servizio di Ragioneria', '2#Servizio Tributi', '3#Servizio Personale', '4#Servizio Segreteria', '5#Servizio Anagrafe'], 'mailS': ['1#ragioneria@pec.comune.avio.tn.it', '2#tributi@pec.comune.avio.tn.it', '3#personale@pec.comune.avio.tn.it', '4#segreteria@pec.comune.avio.tn.it', '5#anagrafe@pec.comune.avio.tn.it'], 'mailSPub': ['1#s', '2#s', '3#s', '4#s', '5#s']}

{'objectClass': ['top', 'organization', 'amministrazione'], 'o': ['c_a986'], 'tipoAmm': 'L6', 'logoAmm': 'c_a986.gif', 'description': ['Comune di Bordolano'], 'postalCode': ['26020'], 'l': ['Bordolano'], 'provincia': 'CR', 'regione': 'Lombardia', 'nomeResp': 'Davide', 'cognomeResp': 'Brena', 'titoloResp': 'Sindaco', 'sitoIstituzionale': 'www.comune.bordolano.cr.it', 'st': ['ACCREDITATA'], 'dataVerifica': '2018-06-05', 'codiceFiscaleAmm': '00305100190', 'codiceAmm': '125152500201', 'street': ['Via Maggiore, 16'], 'macroTipoAmm': 'PA', 'mail': ['bordolano@postemailcertificata.it'], 'fruibS': ['1#false'], 'mailS': ['1#sindaco@comunebordolano.it'], 'telephonenumberS': ['1#037295926'], 'mailSPub': ['1#s']}

# Come funzioano gli enti cessati?
 {'objectClass': ['top', 'organization', 'amministrazione'], 'o': ['isiao'], 'tipoAmm': 'C7', 'logoAmm': 'isiao.gif', 'dominioPEC': 'pec.it', 'description': ["Istituto Italiano per l'Africa e l'Oriente"], 'postalCode': ['00197'], 'l': ['Roma'], 'provincia': 'RM', 'regione': 'Lazio', 'nomeResp': 'Gherardo', 'cognomeResp': 'Gnoli', 'sitoIstituzionale': 'www.isiao.it', 'st': ['ACCREDITATA'], 'dataVerifica': '2011-04-18', 'codiceAmm': '113090009201', 'street': ['Via Ulisse Aldrovandi, 16'], 'macroTipoAmm': 'PA', 'mail': ['amministrazione.isiao@pec.it']}

"""


def test_empty():
    l = Location()
    l.json()
    y = l.yaml()
    assert yaml.load(y) == {}
    assert is_empty(l)


def test_dump_empty():
    l = Location()
    a = Location()
    a.cap = l
    j = a.json()
    assert j == "{}"


def test_pa_latina():
    ret = Amministrazione.from_ldap(**c_e472)
    yield print, ret.yaml()
    assert ret.location.cap == "04100"
    assert ret.codice_ipa == "c_e472"
    assert len(ret.servizi) == 7


def test_entry_servizio():
    for e in (c_e472, uc_trento, AvvStudioA_c_e472):
        ret = Servizio.from_ldap(**e)
        for x in ret:
            yield print, x.yaml(), yaml.dump(e)


def test_entry_ufficio():
    for u in (umc_latina_m_inf, ced_c_e472):
        for ret in harn_entry_ufficio(ufficio=u):
            yield ret


def harn_entry_ufficio(ufficio):
    for Cls in (FatturazioneElettronica, Responsabile, Location, Ufficio):
        ret = Cls.from_ldap(**ufficio)
        yield print, ret.yaml()


def test_pa():
    for a in (c_e472, uc_trento):
        a = Amministrazione.from_ldap(**a)
        yield print, a.yaml()


def test_all_pa():
    c = connect()
    c.search(
        search_base="c=it",
        search_scope=1,
        attributes="*",
        size_limit=10,
        search_filter="(&(objectclass=amministrazione)(codiceFiscaleAmm=*))",
    )
    for entry in c.response:
        x = entry["attributes"]
        # print("=" * 40, x)
        try:
            a = Amministrazione.from_ldap(**x)
            log.debug(a.yaml())
        except:
            log.warning("Errore processando ente: {}", x)


def test_all_aoo():
    # aoo=SUAP,o=c_e472,c=it
    c = connect()
    c.search(
        search_base="c=it",
        search_scope=2,
        attributes="*",
        size_limit=10,
        search_filter="(&(objectclass=aoo)(o=c_e472))",
    )
    for entry in c.response:
        x = entry["attributes"]
        print("=" * 40, x)
        try:
            a = AOO.from_ldap(dn=entry["dn"], **x)
            print(a.yaml())
        except (IndexError,):
            log.warning("Errore processando ente: {}", x)


def test_all_ufficio():
    # aoo=SUAP,o=c_e472,c=it
    c = connect()
    c.search(
        search_base="c=it",
        search_scope=2,
        attributes="*",
        size_limit=10,
        search_filter="(&(objectclass=ufficio)(o=c_e472))",
    )
    for entry in c.response:
        x = entry["attributes"]
        print("=" * 40, x)
        try:
            a = Ufficio.from_ldap(dn=entry["dn"], **x)
            print(a.yaml())
        except (IndexError,):
            log.warning("Errore processando ente: {}", x)


def test_common_fields_from_entries():

    ret = Location.from_ldap(**c_e472)
    yield print, ret.json()
    yield assert_equals, ret.cap, "04100"

    ret = Responsabile.from_ldap(**c_e472)
    yield print, ret.json()
    yield assert_equals, ret.telefono, "077346631"


def notest_login3():
    connect()


def notest_search_latina3():
    c = connect()
    c.search(
        search_base="c=it",
        search_scope=2,
        attributes="*",
        size_limit=10,
        search_filter="(o=c_e472)",
    )
    for entry in c.response:
        x = entry["attributes"]
        print("=" * 40, x)
        try:
            print("location", Location.from_ldap(**x).json())
            print("responsabile", Responsabile.from_ldap(**x).json())
        except:
            raise
