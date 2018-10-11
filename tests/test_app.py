# coding: utf-8

from test_config import BaseTestCase

LIST_FIELDS = ('count', 'limit', 'items')


class TestIPA(BaseTestCase):
    """PublicController integration test stubs"""


    def test_list_amministrazioni(self):
        response = self.client.open(
            '/ipa/v0/amministrazioni?limit=1',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        for field in LIST_FIELDS:
            assert field in response.json

        assert response.json.get('count') == 1
        entry = response.json['items'][0]
        assert 'self' in entry['links']

        for related_link in ('uffici', 'aree_amministrative_omogenee'):
            assert any(related_link in u for u in entry['links']['related'])

    def test_list_aoo(self):
        response = self.client.open(
            '/ipa/v0/amministrazione/c_e472/aree_organizzative_omogenee?limit=2',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        assert 'items' in response.json
        assert response.json.get('count') == 2

        entry = response.json['items'][0]
        assert all(f in entry['links'] for f in ('self', 'parent'))


    def test_list_uffici(self):
        response = self.client.open(
            '/ipa/v0/amministrazione/c_e472/uffici?limit=2',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        assert response.json.get('count') == 2
        assert all(field in response.json for field in LIST_FIELDS)
        entry = response.json['items'][0]
        assert all(f in entry['links'] for f in ('self', 'parent'))


    def test_get_pa(self):
        response = self.client.open('/ipa/v0/amministrazione/c_e472', method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        entry = response.json
        assert all(f in entry['links'] for f in ('self', 'related'))


    def test_get_aoo(self):
        response = self.client.open(
            '/ipa/v0/amministrazione/c_e472/area_organizzativa_omogenea/aooser9.2',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        entry = response.json
        assert all(f in entry['links'] for f in ('self', 'parent'))

    def test_get_ufficio(self):
        response = self.client.open(
            '/ipa/v0/amministrazione/c_e472/ufficio/KF05EG',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        entry = response.json
        assert all(f in entry['links'] for f in ('self', 'parent'))
