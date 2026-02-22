from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .views import rag_chat, DocumentViewSet

urlpatterns = [

    path("admin/", admin.site.urls),

    # Authentication
    path("api/token/", TokenObtainPairView.as_view()),
    path("api/token/refresh/", TokenRefreshView.as_view()),

    # Documentation
    path("api/schema/", SpectacularAPIView.as_view()),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),

    # Documents API
    path(
        "api/v1/documents/",
        DocumentViewSet.as_view({
            "get": "list",
            "post": "create"
        })
    ),

    # Chat API
    path("chat/", rag_chat),
]