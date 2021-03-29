from django.conf.urls import url
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view


schema_view = get_schema_view(
    openapi.Info(
        title="Candy Delivery App",
        default_version="0.0.1",
        description="API for study project",
        license=openapi.License(name="BSD License"),
    ),
    patterns=[path("", include("api.urls"))],
    public=False,
    permission_classes=tuple(),
    authentication_classes=tuple(),
)

urlpatterns = [
    path("", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    url(
        r"^schema(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
]
