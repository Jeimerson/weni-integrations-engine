from rest_framework import viewsets
from rest_framework.decorators import action
from django.conf import settings

from marketplace.applications.models import App
from .serializers import TelegramSerializer
from marketplace.accounts.permissions import ProjectManagePermission
from marketplace.celery import app as celery_app
from . import type as type_


class TelegramViewSet(viewsets.ModelViewSet):

    queryset = App.objects
    serializer_class = TelegramSerializer
    lookup_field = "uuid"
    permission_classes = [ProjectManagePermission]

    def get_queryset(self):
        return super().get_queryset().filter(code=type_.TelegramType.code)

    def perform_create(self, serializer):
        serializer.save(code=type_.TelegramType.code)

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        if settings.USE_GRPC:  # This is provisional, to enable unit testing
            celery_app.send_task(
                name="release_channel", args=[instance.config.get("channelUuid"), self.request.user.email]
            ).wait()

    @action(detail=True, methods=["PATCH"])
    def configure(self, request, **kwargs):
        ...