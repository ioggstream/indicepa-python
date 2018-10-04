from dataclasses import dataclass

from nose.tools import assert_set_equal

from ipa.api_filter import parse_filter
from ipa.model import Amministrazione, Location
from test_config import connect, log


@dataclass
class TestCase:
    q_filter: str
    ldap_attributes: set


def test_simple():
    t = TestCase(
        q_filter="codice_ipa,codice_fiscale", ldap_attributes=["o", "codiceFiscaleAmm"]
    )
    assert parse_filter(t.q_filter) == t.ldap_attributes


def test_complex():
    t = TestCase(
        q_filter="codice_ipa,codice_fiscale,location",
        ldap_attributes={"o", "codiceFiscaleAmm"} | set(Location.q_fields().values()),
    )
    assert_set_equal(set(parse_filter(t.q_filter)), t.ldap_attributes)


def test_all_pa():
    c = connect()
    c.search(
        search_base="c=it",
        search_scope=1,
        attributes=parse_filter("codice_ipa,codice_fiscale,descrizione"),
        size_limit=10,
        search_filter="(&(objectclass=amministrazione)(codiceFiscaleAmm=*))",
    )
    for entry in c.response:
        x = entry["attributes"]
        # print("=" * 40, x)
        try:
            a = Amministrazione.from_ldap(**x)
            log.debug(a.yaml())
        except Exception:
            log.exception("Errore processando ente: %s", entry)
