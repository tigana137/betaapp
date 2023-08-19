from django.urls import path
from . import views


urlpatterns = [
    path('test/', views.test,name='test'),
    path('verify_school_id/<str:pk>',views.verify_school_id, name='verify_school_id'),
    path('verify_logins/', views.verify_logins,name='verify_logins'),
    path('initiate_data/', views.initiate_data,name='initiate_data')
]
