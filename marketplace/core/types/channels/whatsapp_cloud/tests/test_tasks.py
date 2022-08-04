from uuid import uuid4
from typing import TYPE_CHECKING
from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from marketplace.core.types import APPTYPES
from ..tasks import sync_whatsapp_cloud_apps
from marketplace.applications.models import App


if TYPE_CHECKING:
    from unittest.mock import MagicMock


User = get_user_model()


class SyncWhatsAppCloudAppsTaskTestCase(TestCase):
    def setUp(self) -> None:

        wpp_type = APPTYPES.get("wpp-cloud")
        wpp_cloud_type = APPTYPES.get("wpp-cloud")

        self.wpp_app = wpp_type.create_app(
            config={},
            project_uuid=uuid4(),
            flow_object_uuid=uuid4(),
            created_by=User.objects.get_admin_user(),
        )

        self.wpp_cloud_app = wpp_cloud_type.create_app(
            config={},
            project_uuid=uuid4(),
            flow_object_uuid=uuid4(),
            created_by=User.objects.get_admin_user(),
        )

        return super().setUp()

    def _get_mock_value(self, project_uuid: str, flow_object_uuid: str) -> list:
        return [
            {
                "channel_data": {
                    "project_uuid": project_uuid,
                    "channels": [
                        {"uuid": flow_object_uuid, "name": "Fake Name", "config": "{}", "address": "+55829946542"}
                    ],
                }
            }
        ]

    @patch("marketplace.connect.client.ConnectProjectClient.list_channels")
    def test_whatsapp_app_that_already_exists_is_migrated_correctly(self, list_channel_mock: "MagicMock") -> None:
        list_channel_mock.return_value = self._get_mock_value(
            str(self.wpp_app.project_uuid), str(self.wpp_app.flow_object_uuid)
        )

        sync_whatsapp_cloud_apps()

        app = App.objects.get(id=self.wpp_app.id)
        self.assertEqual(app.code, "wpp-cloud")

    @patch("marketplace.connect.client.ConnectProjectClient.list_channels")
    def test_create_new_whatsapp_cloud(self, list_channel_mock: "MagicMock") -> None:
        project_uuid = str(uuid4())
        flow_object_uuid = str(uuid4())

        list_channel_mock.return_value = self._get_mock_value(project_uuid, flow_object_uuid)

        sync_whatsapp_cloud_apps()

        self.assertTrue(App.objects.filter(flow_object_uuid=flow_object_uuid).exists())
        self.assertTrue(App.objects.filter(project_uuid=project_uuid).exists())
