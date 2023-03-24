"""Client for connection with flows"""
import requests

from django.conf import settings

from rest_framework.exceptions import APIException


class FlowsClient:
    def __init__(self):
        self.base_url = settings.FLOWS_REST_ENDPOINT
        self.authentication_instance = InternalAuthentication()

    def list_channel_types(self, channel_code):
        # TODO: Change request structure to use make_request method
        if channel_code:
            request_url = (
                f"{self.base_url}/api/v2/internals/channels/{str(channel_code)}"
            )
        else:
            request_url = f"{self.base_url}/api/v2/internals/channels"

        response = requests.get(
            url=request_url, headers=self.authentication_instance.headers, timeout=60
        )
        return response

    def detail_channel(self, flow_object_uuid):
        url = f"{self.base_url}/api/v2/internals/channel/{str(flow_object_uuid)}"

        response = self.make_request(
            url, method="GET", headers=self.authentication_instance.headers
        )
        return response.json()

    def update_config(self, data, flow_object_uuid):
        payload = {"config": data}
        url = f"{self.base_url}/api/v2/internals/channel/{flow_object_uuid}/"

        response = self.make_request(
            url,
            method="PATCH",
            headers=self.authentication_instance.headers,
            data=payload,
        )
        return response

    def make_request(self, url: str, method: str, headers=None, data=None):
        try:
            response = requests.request(
                method=method, url=url, headers=headers, json=data, timeout=60
            )
            response.raise_for_status()

        except requests.exceptions.HTTPError as exception:
            # Handles HTTP exceptions
            raise APIException(
                detail=f"HTTPError: {str(exception)}", code=response.status_code
            ) from exception
        except requests.exceptions.RequestException as exception:
            # Handle general network exceptions
            raise APIException(
                detail=f"RequestException: {str(exception)}", code=response.status_code
            ) from exception

        return response


class InternalAuthentication:
    def __get_module_token(self):
        try:
            request = requests.post(
                url=settings.OIDC_OP_TOKEN_ENDPOINT,
                data={
                    "client_id": settings.OIDC_RP_CLIENT_ID,
                    "client_secret": settings.OIDC_RP_CLIENT_SECRET,
                    "grant_type": "client_credentials",
                },
                timeout=60,
            )
            request.raise_for_status()

        except requests.exceptions.HTTPError as exception:
            # Handles HTTP exceptions
            raise APIException(
                detail=f"HTTPError: {str(exception)}", code=request.status_code
            ) from exception
        except requests.exceptions.RequestException as exception:
            # Handle general network exceptions
            raise APIException(
                detail=f"RequestException: {str(exception)}", code=request.status_code
            ) from exception

        token = request.json().get("access_token")

        return f"Bearer {token}"

    @property
    def headers(self):
        return {
            "Content-Type": "application/json; charset: utf-8",
            "Authorization": self.__get_module_token(),
        }