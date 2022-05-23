import json
import requests

from django.conf import settings
from rest_framework import serializers

from marketplace.celery import app as celery_app

class ConnectAuth:
    bearer_token = ""

    def get_auth_token(self) -> str:
        request = requests.post(
            url=settings.OIDC_OP_TOKEN_ENDPOINT,
            data={
                "client_id": settings.OIDC_RP_CLIENT_ID,
                "client_secret": settings.OIDC_RP_CLIENT_SECRET,
                "grant_type": "client_credentials",
            },
        )
        token = request.json().get("access_token")
        self.bearer_token = "Bearer {token}"


    def auth_header(self, headers: dict = {}) -> dict:
        if 'Authorization' not in headers:
            headers['Authorization'] = self.bearer_token
        return headers

class ConnectProjectClient(ConnectAuth):

    base_url = settings.CONNECT_ENGINE_BASE_URL

    def list_channels(self, channeltype_code: str):
        payload = {
            "channel_type": channeltype_code
        }
        request = requests.get(url=self.base_url + '/organization/project/list_channel/', json=payload, headers=self.auth_header())
        return json.loads(request.text)

    def create_channel(self, user: str, project_uuid: str, data: dict, channeltype_code: str) -> dict:
        payload = {
            "user": user,
            "project_uuid": project_uuid,
            "data": data,
            "channeltype_code": channeltype_code
        }
        request = requests.post(url=self.base_url + '/organization/project/create_channel/', json=payload, headers=self.auth_header())

        return json.loads(request.text)

    def release_channel(self, channel_uuid: str, user_email: str) -> None:
        payload = {
            "channel_uuid": channel_uuid,
            "user": user_email
        }
        request = requests.post(url=self.base_url + '/organization/project/release_channel/', json=payload, headers=self.auth_header())
        return None


class WPPRouterChannelClient(ConnectAuth):
    base_url = settings.ROUTER_BASE_URL
    
    def get_channel_token(self, uuid: str, name: str) -> str:
        payload = {
            "channel_uuid": uuid,
            "user": name
        }

        request = requests.post(url=self.base_url + '/integrations/channel', json=payload, headers=self.auth_header())
        return json.loads(request)['token']