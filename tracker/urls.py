from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('entries/', views.entry_list, name='entry_list'),
    path('entries/<int:pk>/edit/', views.entry_update, name='entry_update'),
    path('entries/<int:pk>/delete/', views.entry_delete, name='entry_delete'),
]
