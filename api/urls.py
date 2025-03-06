from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views  # 確保這個 View 存在

router = DefaultRouter()
router.register(r'test', views.TestModelViewSet)

urlpatterns = [
    path('', include(router.urls)),
]