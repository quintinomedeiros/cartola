import requests
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

class CartolaFCError(Exception):
    pass

def convert_team_name_to_slug(nome):
    pass

class Api(object):
    def __init__(self, email, password, attempts=1):
        self._api_url = 'https://api.cartolafc.globo.com'
        self._auth_url = 'https://login.globo.com/api/authentication'
        self._email = email
        self._password = password
        self._glb_id = None
        self.attempts = attempts if isinstance(attempts, int) and attempts > 0 else 1

        if not email or not password:
            raise CartolaFCError('E-mail ou senha ausente')

        self.set_credentials(email, password)

    def set_credentials(self, email, password):
        response = requests.post(
            self._auth_url,
            json=dict(payload=dict(email='quintinomedeiros@yahoo.com.br', password='972571Df', serviceId=4728))
        )
        if response.status_code == 200:
            self._glb_id = response.json()['glbId']
        else:
            raise CartolaFCError(response.json()['userMessage'])

    def _request(self, url, params=None):
        attempts = self.attempts
        while attempts:
            try:
                headers = {'X-GLB-Token': self._glb_id} if self._glb_id else None
                response = requests.get(url, params=params, headers=headers)
                if self._glb_id and response.status_code == 401:
                    self.set_credentials(self._email, self._password)
                    response = requests.get(url, params=params, headers={'X-GLB-Token': self._glb_id})
                
                if response.status_code == 200 and response.content:
                    return response.json()
                else:
                    raise CartolaFCError('Erro na solicitação HTTP')
            except CartolaFCOverloadError as error:
                attempts -= 1
                if not attempts:
                    raise error

    def mercado(self):
        url = f'{self._api_url}/mercado/status'
        data = self._request(url)
        return data

    def time(self, id=None, nome=None, slug=None):
        if not any((id, nome, slug)):
            raise CartolaFCError('Você precisa informar o nome ou o slug do time que deseja obter')

        param = 'id' if id else 'slug'
        value = id if id else (slug if slug else convert_team_name_to_slug(nome))
        url = f'{self._api_url}/time/{param}/{value}'
        data = self._request(url)
        return data

    def exportar_excel(self, dados, nome_arquivo):
        df = pd.DataFrame(dados)
        wb = Workbook()
        ws = wb.active

        for row in dataframe_to_rows(df, index=False, header=True):
            ws.append(row)

        wb.save(nome_arquivo)

api = Api(email='seu_email', password='sua_senha')

# Exemplo de uso para exportar dados do mercado para um arquivo Excel
mercado = api.mercado()
api.exportar_excel(mercado, 'mercado.xlsx')
