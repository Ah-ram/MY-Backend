from django.urls import path, include
from rest_framework.routers import DefaultRouter

from purchase.controller.views import PurchaseView

router = DefaultRouter()
router.register(r'purchase', PurchaseView, basename='purchase')

urlpatterns = [
    path('', include(router.urls)),
    path('create', PurchaseView.as_view({'post': 'createPurchase'}), name='purchase-create'),
    path('check-is-subscribe', PurchaseView.as_view({'post': 'checkIsSubscribe'}), name='check-is-subscribe'),
]
