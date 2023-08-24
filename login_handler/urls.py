from django.urls import path
from . import views


urlpatterns = [
    path('test/', views.test, name='test'),
    path('verify_school_id/<str:pk>',views.verify_school_id, name='verify_school_id'),
    path('verify_logins/', views.verify_logins, name='verify_logins'),
    path('initiate_data/', views.initiate_data, name='initiate_data'),  # tansech tbadlha
    path('initiate_data2/', views.initiate_data_to_fronent, name='initiate_data'),
    path('presetup/get_all_classes/<str:sid>',views.get_all_classes, name='get_all_classes/'),
    path('presetup/get_working_profs/<str:sid>',views.get_working_profs, name='get_working_profs/'),

    path('presetup/get_eleves_ofClass_array/<str:sid>',
         views.get_eleves_ofClass_array, name='get_eleves_ofClass_array'),
    path('presetup/get_profs_ofClass_array/<str:sid>',
         views.get_profs_ofClass_array, name='get_profs_ofClass_array'),
    path('del_all/',
         views.del_all, name='del_all'),     # ~ na7i zok omha
    path('FinalSave/',
         views.FinalSave, name='FinalSave'),
]

"http://localhost:8000/login_handler/test/"
"http://localhost:8000/login_handler/verify_school_id/843422?format=json"
"http://localhost:8000/login_handler/verify_logins/?format=json"
"http://localhost:8000/login_handler/initiate_data/"
"http://localhost:8000/login_handler/initiate_data2/?format=json"
"http://localhost:8000/login_handler/add_new_class/?format=json"
"http://localhost:8000/login_handler/del_class/?format=json"
"http://localhost:8000/login_handler/presetup/get_all_classes/842920"
"http://localhost:8000/login_handler/presetup/get_eleves_ofClass_array/842920"
"http://localhost:8000/login_handler/presetup/get_working_profs/842920"
"http://localhost:8000/login_handler/presetup/get_profs_ofClass_array/842920"
"http://localhost:8000/login_handler/FinalSave/?format=json"


"http://localhost:8000/login_handler/del_all/"

{
    "saisieprenom": "محرز",
    "saisienom": "بن هلال",
    "saisiepasswd": "مدرستي",
    "login": "843422",
    "mp": "rB3Mv1"
}


{
    "saisie_niveau": "0",
    "saisie_creat_classe": "101",
    "saisie_classe_long": "class whole id i guess",
    "create": "تسجيل"

}


{"saisie_classe_supp": "148"}


# verif_preparation_annuelle()   voir vocal-memo
