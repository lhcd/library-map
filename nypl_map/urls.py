from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/current_library_data', views.library_map_data, name='library_map_data'),
    path('nyc_geo_json', views.nyc_geo_json, name='geo_json'),
    path('library/<int:library_id>/', views.library, name='library'),
]