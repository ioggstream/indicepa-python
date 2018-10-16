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
from samples import (
    AvvStudioA_c_e472,
    c_e472,
    ced_c_e472,
    uc_trento,
    umc_latina_m_inf,
)
from test_config import connect

logging.basicConfig(level=logging.DEBUG)


log = logging.getLogger()


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
            log.warning("Errore processando ente: %r", x)


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
            log.warning("Errore processando ente: %r", x)


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
