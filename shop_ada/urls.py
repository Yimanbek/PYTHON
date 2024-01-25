"""
URL configuration for shop_ada project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path , include 
from rest_framework.routers import DefaultRouter
from category.views import CategoryViewSet
from product.views import ProductViewSet
from django.conf.urls.static import static
from django.conf import settings
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

router = DefaultRouter()
router.register('categories', CategoryViewSet)
router.register('products', ProductViewSet)

schema_view = get_schema_view(
    openapi.Info(title = 'shop_ada0',
    description = 'Book_store',
    default_version='v1',
    ),
    public=True
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/account/', include('account.urls')),
    path('api/', include(router.urls)),
    path('api/order/',include('order.urls')),
    path('docs/',schema_view.with_ui('swagger'))

]
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
