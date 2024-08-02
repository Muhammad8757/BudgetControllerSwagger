from django.urls import path, include
from rest_framework.routers import DefaultRouter
from budget_controller_app.views import UserAPIView, CategoryAPIView, UserTransactionAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

router = DefaultRouter()
router.register(r'users', UserAPIView, basename='user')
router.register(r'categories', CategoryAPIView, basename='category')
router.register(r'transactions', UserTransactionAPIView, basename='transaction')

urlpatterns = [
    path('api/v1/', include(router.urls)),
    
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # Путь для Swagger UI
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # Путь для Redoc UI
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]