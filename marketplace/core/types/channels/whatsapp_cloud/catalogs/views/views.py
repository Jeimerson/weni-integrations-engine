from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status

from marketplace.core.types.channels.whatsapp_cloud.services.facebook import (
    FacebookService,
)
from marketplace.core.types.channels.whatsapp_cloud.services.flows import (
    FlowsService,
)
from marketplace.wpp_products.models import Catalog
from marketplace.applications.models import App

from marketplace.clients.facebook.client import FacebookClient
from marketplace.clients.flows.client import FlowsClient

from marketplace.wpp_products.serializers import (
    CatalogSerializer,
    ToggleVisibilitySerializer,
    TresholdSerializer,
    CatalogListSerializer,
)


class BaseViewSet(viewsets.ModelViewSet):
    fb_service_class = FacebookService
    fb_client_class = FacebookClient

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fb_service = None

    @property
    def fb_service(self):  # pragma: no cover
        if not self._fb_service:
            self._fb_service = self.fb_service_class(self.fb_client_class())
        return self._fb_service


class Pagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = "page_size"
    max_page_size = 500


class CatalogViewSet(BaseViewSet):
    serializer_class = CatalogSerializer
    pagination_class = Pagination

    def filter_queryset(self, queryset):
        params = self.request.query_params
        name = params.get("name")
        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset

    def get_queryset(self):
        app_uuid = self.kwargs.get("app_uuid")
        app = get_object_or_404(App, uuid=app_uuid, code="wpp-cloud")
        return Catalog.objects.filter(app=app).order_by("name")

    def get_object(self):
        queryset = self.get_queryset()
        catalog_uuid = self.kwargs.get("catalog_uuid")
        return get_object_or_404(queryset, uuid=catalog_uuid)

    def retrieve(self, request, *args, **kwargs):
        catalog = self.get_object()
        connected_catalog_id = self.fb_service.get_connected_catalog(catalog.app)
        serializer = self.serializer_class(
            catalog, context={"connected_catalog_id": connected_catalog_id}
        )
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page_data = self.paginate_queryset(queryset)
        serialized_data = []

        if queryset.exists():
            connected_catalog_id = self.fb_service.get_connected_catalog(
                queryset.first().app
            )
            serializer = CatalogListSerializer(
                page_data, context={"connected_catalog_id": connected_catalog_id}
            )
            serialized_data = serializer.data

        return self.get_paginated_response(serialized_data)

    @action(detail=True, methods=["POST"])
    def enable_catalog(self, request, *args, **kwargs):
        response = self.fb_service.enable_catalog(self.get_object())
        return Response(response)

    @action(detail=True, methods=["POST"])
    def disable_catalog(self, request, *args, **kwargs):
        response = self.fb_service.disable_catalog(self.get_object())
        return Response(response)


class CommerceSettingsViewSet(BaseViewSet):
    serializer_class = ToggleVisibilitySerializer

    @action(detail=False, methods=["GET"])
    def commerce_settings_status(self, request, app_uuid, *args, **kwargs):
        app = get_object_or_404(App, uuid=app_uuid, code="wpp-cloud")
        response = self.fb_service.wpp_commerce_settings(app)
        return Response(response)

    @action(detail=False, methods=["POST"])
    def toggle_catalog_visibility(self, request, app_uuid, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        enable_visibility = serializer.validated_data["enable"]

        app = get_object_or_404(App, uuid=app_uuid, code="wpp-cloud")
        response = self.fb_service.toggle_catalog_visibility(app, enable_visibility)
        return Response(response)

    @action(detail=False, methods=["POST"])
    def toggle_cart_visibility(self, request, app_uuid, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        enable_cart = serializer.validated_data["enable"]

        app = get_object_or_404(App, uuid=app_uuid, code="wpp-cloud")
        response = self.fb_service.toggle_cart(app, enable_cart)
        return Response(response)

    @action(detail=False, methods=["GET"])
    def get_active_catalog(self, request, app_uuid, *args, **kwargs):
        app = get_object_or_404(App, uuid=app_uuid, code="wpp-cloud")
        response = self.fb_service.get_connected_catalog(app)
        return Response(response)


class TresholdViewset(BaseViewSet):
    serializer_class = TresholdSerializer

    flows_service_class = FlowsService
    flows_client_class = FlowsClient

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._flows_service = None

    @property
    def flows_service(self):  # pragma: no cover
        if not self._flows_service:
            self._flows_service = self.flows_service_class(self.flows_client_class())
        return self._flows_service

    @action(detail=True, methods=["POST"])
    def update_treshold(self, request, app_uuid, *args, **kwargs):
        app = get_object_or_404(App, uuid=app_uuid, code="wpp-cloud")
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        treshold = serializer.validated_data["treshold"]
        self.flows_service.update_treshold(app, treshold)

        return Response(status=status.HTTP_204_NO_CONTENT)
