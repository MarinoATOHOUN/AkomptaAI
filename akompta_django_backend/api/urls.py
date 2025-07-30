from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    ProductViewSet,
    SaleViewSet,
    ExpenseViewSet,
    SavingsViewSet,
    StockMovementViewSet,
    ReportViewSet,
)

router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"products", ProductViewSet)
router.register(r"sales", SaleViewSet)
router.register(r"expenses", ExpenseViewSet)
router.register(r"savings", SavingsViewSet)
router.register(r"stock-movements", StockMovementViewSet)
router.register(r"reports", ReportViewSet)

urlpatterns = [
    path("", include(router.urls)),
]




from .views import register_user, login_user, verify_token, process_voice_command, get_dashboard_summary
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView,)

urlpatterns += [
    path("auth/register/", register_user, name="register"),
    path("auth/login/", login_user, name="login"),
    path("auth/verify-token/", verify_token, name="verify_token"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("voice/process/", process_voice_command, name="process_voice_command"),
    path("dashboard/summary/", get_dashboard_summary, name="dashboard_summary"),
]


