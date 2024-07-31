from django.urls import path, include
from rest_framework.routers import DefaultRouter
from budget_controller_app.views import UserAPIView, CategoryAPIView, UserTransactionAPIView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

schema_view = get_schema_view(
    openapi.Info(
        title="Budger controller api",
        default_version='v1',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register(r'users', UserAPIView, basename='user')
router.register(r'categories', CategoryAPIView, basename='category')
router.register(r'transactions', UserTransactionAPIView, basename='transaction')

urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0),
         name='schema-redoc'),
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]