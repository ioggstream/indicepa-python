import json
import logging
from collections import defaultdict
from datetime import datetime

import yaml
from dataclasses import asdict, dataclass, field, fields, is_dataclass

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def is_empty(v):
    if v is None:
        return True
    if v == "null":
        return True
    if isinstance(v, JsonMixin):
        return v.empty()
    return not bool(v)


def remove_nulls(d):
    return {k: v for k, v in d.items() if not is_empty(v)}


class JsonMixin(object):
    def __init__(self):
        self.links: list = None
        self._mappa_campi = {}

    @property
    def id(self):
        if is_dataclass(self):
            f_name = fields(self)[0].name
            return getattr(self, f_name)
        raise TypeError("Should be dataclass")

    @classmethod
    def q_fields(cls):
        return {v[0]: k for k, v in cls._mappa_campi.items()}

    def empty(self):
        return json.loads(self.json()) == {}

    def json(self):
        # XXX This could be optimized
        ret = json.loads(json.dumps(asdict(self)), object_hook=remove_nulls)
        if hasattr(self, "links"):
            ret.update({"links": self.links})
        return json.dumps(ret)

    def yaml(self):
        return yaml.dump(yaml.load(self.json()), default_flow_style=0)


@dataclass
class FatturazioneElettronica(JsonMixin):
    """
     'canaleTrasmissivoSFE': 'SPCOOP',
     'nomeSFE': 'FATTURAZIONE',
     'intermediarioSFE': 'si',
     'URISFE': 'https://MinisteroEconomiaFinanze.spcoop.gov.it/openspcoop/PA/MEF/DFP_SIFE_RicezioneFatture_1',
     'codiceFiscaleSFE': '80007830591',
     'dataVerificaCFSFE': '2014-04-10',
     'dataAvvioSFE': '2014-06-06'

    """

    nome: str = None
    # NB: il codiceFiscale della Fatturazione Elettronica non è necessariamente
    #     quello dell'ente
    codiceFiscale: str = None
    canaleTrasmissivo: str = None
    dataAvvio: datetime = None
    dataVerificaCodiceFiscale: datetime = None
    uri: str = None
    intermediario: str = None
    mail: str = None
    pec: str = None

    _mappa_campi = {
        "nomeSFE": "nome",
        "URISFE": "uri",
        "canaleTrasmissivoSFE": "canaleTrasmissivo",
        "codiceFiscaleSFE": "codiceFiscale",
        "dataVerificaCFSFE": "dataVerificaCodiceFiscale",
        "dataAvvioSFE": "dataAvvio",
        "mailSFE": "mail",
        "mailSFEPEC": "pec",
        "intermediarioSFE": "intermediario",
    }

    @classmethod
    def from_ldap(cls, **kwargs):

        d = {
            cls._mappa_campi[ldap_k]: ldap_v
            for ldap_k, ldap_v in kwargs.items()
            if ldap_k in cls._mappa_campi
        }
        return FatturazioneElettronica(**d)


@dataclass
class Responsabile(JsonMixin):
    """
    Una persona Responsabile. Può essere di struttura, di SFE, ...
    """

    nome_proprio: str = None
    cognome: str = None
    titolo: str = None
    mail: str = None
    telefono: str = None

    _mappa_campi = {
        "MailRespSFE": "mail",
        "cognomeResp": "cognome",
        "nomeResp": "nome_proprio",
        "telephonenumberRespSFE": "telefono",
        "titoloResp": "titolo",
    }

    @classmethod
    def from_ldap(cls, **kwargs):

        d = {
            cls._mappa_campi[ldap_k]: ldap_v
            for ldap_k, ldap_v in kwargs.items()
            if ldap_k in cls._mappa_campi
        }
        return Responsabile(**d)


@dataclass
class Location(JsonMixin):
    indirizzo: str = None
    cap: str = None
    comune: str = None
    provincia: str = None
    regione: str = None

    _mappa_campi = {
        "street": ("indirizzo", "".join),
        "postalCode": ("cap", "".join),
        "l": ("comune", "".join),
        "provincia": ("provincia", None),
        "regione": ("regione", None),
    }

    @classmethod
    def from_ldap(cls, **kwargs):
        """

        'street': ['Strada Congiunte Destre'],
        'postalCode': ['04100'],
        'l': ['Latina'],
        'provincia': 'LT',
        'regione': 'Lazio',

        """

        d = {}
        for ldap_k, ldap_v in kwargs.items():
            if ldap_v == "null":
                continue
            if ldap_k not in cls._mappa_campi:
                continue
            ipa_k, formatter = cls._mappa_campi[ldap_k]

            d.update({ipa_k: formatter(ldap_v) if formatter else ldap_v})
        return Location(**d)


@dataclass
class Ufficio(JsonMixin):
    codice_univoco_ufficio: str
    codice_ipa: str
    descrizione: str
    mail: list = field(default_factory=list)
    contatti: list = field(
        default_factory=list
    )  # FIXME merge mail and contatti
    location: Location = None
    fatturazione: FatturazioneElettronica = None

    _mappa_campi = {
        "o": ("codice_ipa", "".join),
        "CodiceUnivocoUO": ("codice_univoco_ufficio", None),
        "description": ("descrizione", "".join),
        "codiceFiscaleAmm": ("codice_fiscale", None),
        "tipoAmm": ("categoria", None),
        "macroTipoAmm": ("tipologia", None),
        "sitoIstituzionale": ("sito_istituzionale", None),
        "mail": ("mail", None),
    }

    @classmethod
    def from_ldap(cls, **kwargs):
        if "ufficio" not in kwargs.get("objectClass", []):
            raise ValueError("L'entita' non e' un ufficio.")

        d = {}
        for ldap_k, ldap_v in kwargs.items():
            if ldap_v == "null":
                continue
            if ldap_k not in cls._mappa_campi:
                continue
            ipa_k, formatter = cls._mappa_campi[ldap_k]

            d.update({ipa_k: formatter(ldap_v) if formatter else ldap_v})

        a = Ufficio(**d)
        a.location = Location.from_ldap(**kwargs)
        a.responsabile = Responsabile.from_ldap(**kwargs)
        a.fatturazione = FatturazioneElettronica.from_ldap(**kwargs)
        return a


@dataclass
class AOO(JsonMixin):
    """
    dn: aoo=SUAP,o=c_e472,c=it
    objectClass: top
    objectClass: aoo
    aoo: SUAP
    description: Servizio Attivita' Produttive e Suap
    postalCode: 04100
    l: Latina
    provincia: LT
    regione: Lazio
    street: Via Bonn (Trav. Via Varsavia)
    mail: servizio.attivitaproduttive@pec.comune.latina.it
    dataIstituzione: 2018-01-01
    dataSoppressione: 2018-09-04
    nomeResp: Grazia
    cognomeResp: De Simone
    telephoneNumber: 07731757321
    mailResp: grazia.desimone@comune.latina.it
    telephonenumberResp: 07731757342

    """

    codice_aoo: str = None
    codice_ipa: str = None
    descrizione: str = None
    istituita_il: datetime = None
    soppressa_il: datetime = None
    mail: str = None
    location: Location = None
    responsabile: Responsabile = None
    servizi: list = field(default_factory=list)

    _mappa_campi = {
        "dn": ("dn", None),
        "mail": ("mail", None),
        "description": ("descrizione", "".join),
        "dataIstituzione": ("istituita_il", None),
        "dataSoppressione": ("soppressa_il", None),
        "aoo": ("codice_aoo", None),
    }

    @classmethod
    def from_ldap(cls, **kwargs):
        if "aoo" not in kwargs.get("objectClass", []):
            raise ValueError("L'entita' non e' un'AOO.")

        d = {}
        for ldap_k, ldap_v in kwargs.items():
            if ldap_v == "null":
                continue
            if ldap_k not in cls._mappa_campi:
                continue
            ipa_k, formatter = cls._mappa_campi[ldap_k]
            d.update({ipa_k: formatter(ldap_v) if formatter else ldap_v})

        # Il codice_ipa dev'essere passato dall'API.
        d["codice_ipa"] = d["dn"].split(",")[-2][2:]
        del d["dn"]
        a = AOO(**d)
        a.location = Location.from_ldap(**kwargs)
        a.responsabile = Responsabile.from_ldap(**kwargs)
        a.servizi = list(Servizio.from_ldap(**kwargs))
        return a


@dataclass
class Servizio(JsonMixin):
    """XXX Alcune entry hanno descrizione / fruibilita' / nome a None

    """

    nome: str = None
    fruibilita: str = None
    descrizione: str = None
    progressivo: int = 0
    mail: str = None
    url: str = None

    _mappa_campi = {
        "nomeS": "nome",
        "descrizioneS": "descrizione",
        "fruibS": "fruibilita",
        "mailS": "mail",
        "servizioTelematico": "url",
        "telephoneNumberS": "telefono",
    }

    @classmethod
    def from_ldap(cls, **kwargs):

        d = defaultdict(dict)
        for k, values in kwargs.items():
            if k not in cls._mappa_campi:
                continue

            for x in values:
                i, v = x.split("#", 1)
                i = int(i)
                d[i].update({cls._mappa_campi[k]: v, "progressivo": i})

        ret = sorted((i, v) for i, v in d.items())
        for i, v in ret:
            yield Servizio(**v)


@dataclass
class Contatto(JsonMixin):
    mail: str
    tipo: str = None

    @classmethod
    def from_ldap(cls, **kwargs):
        """
        'contatti':  ['protocollo@aslromag.it#altro']
        :param kwargs:
        :return:
        """
        if "contatti" not in kwargs:
            return []
        return [Contatto(*x.split("#")) for x in kwargs["contatti"]]


@dataclass
class Amministrazione(JsonMixin):
    codice_ipa: str
    descrizione: str = None
    codice_fiscale: str = None
    tipologia: str = None
    categoria: str = None
    acronimo: str = None
    sito_istituzionale: str = None
    mail: list = None
    pec: list = None
    location: Location = None
    responsabile: Responsabile = None
    servizi: list = field(default_factory=list)
    contatti: list = field(default_factory=list)

    _mappa_campi = {
        "o": ("codice_ipa", "".join),
        "description": ("descrizione", "".join),
        "codiceFiscaleAmm": ("codice_fiscale", None),
        "tipoAmm": ("categoria", None),
        "sitoIstituzionale": ("sito_istituzionale", None),
        "contatti": ("contatti", None),
        "macroTipoAmm": ("tipologia", None),
        "mail": ("mail", None),
    }

    @classmethod
    def from_ldap(cls, **kwargs):
        d = {}
        for ldap_k, ldap_v in kwargs.items():
            if ldap_v == "null":
                continue
            if ldap_k not in cls._mappa_campi:
                continue
            ipa_k, formatter = cls._mappa_campi[ldap_k]

            d.update({ipa_k: formatter(ldap_v) if formatter else ldap_v})

        a = Amministrazione(**d)
        a.location = Location.from_ldap(**kwargs)
        a.responsabile = Responsabile.from_ldap(**kwargs)
        a.servizi = list(Servizio.from_ldap(**kwargs))
        a.contatti = Contatto.from_ldap(**kwargs)
        return a
