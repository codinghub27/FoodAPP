from . import views
from django.urls import path, include
from django.views.decorators.cache import cache_page

from rest_framework.routers import  DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
router=DefaultRouter()
router.register(r"items",views.ItemViewSet,basename='item')

app_name='myapp'
urlpatterns = [
    #api with DFW
    path('api/token/',TokenObtainPairView.as_view(),name='token_obj_pair'),
    path('api/token/refresh',TokenRefreshView.as_view(),name='token_refresh'),

    path('api/',include(router.urls)),
    # path('api/items/',views.ItemListCreateAPI.as_view(),name='item-list-api'),
    # path('api/items/<int:id>/', views.ItemDetailApiView.as_view(), name='item-detail-api'),

    #views for templates
    path('', views.index,name='index'),
    path('<int:id>/',views.detail,name='detail'),
    path('add/',views.create_item,name='form'),
    path('update/<int:id>',views.update_item,name='update'),
    path('delete/<int:id>',views.delete_item,name='delete'),
]
