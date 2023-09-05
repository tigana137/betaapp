import pprint
from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F, Value
from django.db.models.functions import Concat
from django.db import transaction

from rest_framework.decorators import api_view
from rest_framework.response import Response

from login_handler.second_backend import initiate2

from .models import Ecole_data, Eleves, Classes, ElevesTransfer, Matieres, Matieres, Profs, Logins, Del1, Dre, sexeEleves
from .serializers import Eleves_serializer, Eleves_serializer2, Matiere_serializer, Profs_serializer, classes_serializer, classes_serializer2, ecole_data_serializer
from .views_subfunct import del__class, verify_cnte, verify_stat, add_class
from .backend_algo import chgmentClas1, initiate, nbr_elevs_schools
import requests
import time
from bs4 import BeautifulSoup as bs

from django.http import JsonResponse
from openpyxl import load_workbook
# Create your views here.

dic = {'ecole_url': 'http://www.ent3.cnte.tn/sousse/ahl-jmii/', 'saisieprenom': 'محرز',
       'saisienom': 'بن هلال', 'saisiepasswd': '1925', 'login': '843422', 'mp': 'rB3Mv1', 'sid': '843422'}

# dic = {'ecole_url': 'http://www.ent3.cnte.tn/sousse/el-amal-cite-erriadh/', 'saisieprenom': 'عبد السلام',
#       'saisienom': 'الشرفي', 'saisiepasswd': '06104104', 'login': '842920', 'mp': '', 'sid': '842920'}


@api_view(['GET'])
def del_all(request):
    Matieres.objects.all().delete()
    Profs.objects.all().delete()
    Eleves.objects.all().delete()
    Classes.objects.all().delete()
    ElevesTransfer.objects.all().delete()
    return Response(True)


@api_view(['GET'])
def test(request):
    ecoles = Ecole_data.objects.filter(sid__startswith='84')
    for ecole in ecoles:
        payload = {
            'ecole_url': ecole.url+'/',
            "saisieprenom": ecole.pr_nom,
            "saisienom": ecole.pr_prenom,
            "saisiepasswd": '1234',
            "saisie_membre": "administrateur",
        }
        if verify_cnte(payload):
            print('wowow  :'+str(ecole.sid))
        else:
            print('sid : '+str(ecole.sid) + ' non')
        pass
    return Response(True)


@api_view(['GET'])
# yb3th json file fih l donne l 5dhithom mn ent.env3
def verify_school_id(request, pk):
    try:
        data = Ecole_data.objects.get(sid=pk)
    except Ecole_data.DoesNotExist:
        serializer = ecole_data_serializer(data={'bool': False})
        serializer.is_valid()
        return Response(serializer.data)

    serializer = ecole_data_serializer(data, many=False)
    return Response(serializer.data)


@api_view(['POST'])
# yferivi si l logins t3 l stat s7a7
def verify_logins(request):

    if not verify_cnte(request.data):
        return Response(False)

    if request.data['mp'] != '':
        if not verify_stat(request.data):
            pass
            # return Response(False)

    Logins(ecole_id=request.data['sid'], field='saisieprenom',
           val=str(request.data["saisieprenom"])).save()
    Logins(ecole_id=request.data['sid'], field='saisienom',
           val=str(request.data["saisienom"])).save()
    Logins(ecole_id=request.data['sid'], field='saisiepasswd',
           val=str(request.data["saisiepasswd"])).save()
    Logins(ecole_id=request.data['sid'], field='login',
           val=str(request.data["login"])).save()
    Logins(ecole_id=request.data['sid'], field='mp',
           val=str(request.data["mp"])).save()
    return Response(True)


# zid cond ken virgin walle bch ymchi l intiatevirgin walla nnvirgin
@api_view(['POST'])
def initiate_data(request):
    return Response(True)
    initiate2(request.data)
    def del_all(dic):
        Matieres.objects.filter(ecole_id=dic['sid']).delete()
        Profs.objects.filter(ecole_id=dic['sid']).delete()
        Eleves.objects.filter(ecole_id=dic['sid']).delete()
        Classes.objects.filter(ecole_id=dic['sid']).delete()
        pass
    # del_all(request.data)

    # initiate2(dic)
    # initiate(request.data)
    # sid = request.data['sid']
    # ecole = Ecole_data.objects.get(sid=sid)
    # ecole.virgin=False
    # ecole.save()
    return Response(True)
    # initiate(dic)


@api_view(['GET'])
def initiate_data_to_fronent(request):
    return Response(True)


@api_view(['GET'])
def get_all_classes(request, sid):
    classes_array = []
    for i in range(7):
        classes = Classes.objects.filter(level=i, ecole_id=sid)
        serializer = classes_serializer(classes, many=True)
        classes_array.append(serializer.data)
    return Response(classes_array)


@api_view(['GET'])
def get_all_classes2(request, sid):
    classes_array = []
    for i in range(7):
        classes = Classes.objects.filter(level=i, ecole_id=sid)
        serializer = classes_serializer2(classes, many=True)
        classes_array.append(serializer.data)
    return Response(classes_array)

@api_view(['GET'])
def get_next_classe(request, sid,classe_id):
    eleves =Eleves.objects.filter(ecole_id=sid,next_class_id=classe_id)
    serializer= Eleves_serializer2(eleves,many=True).data
    return Response(serializer)


@api_view(['GET'])
def get_eleves_ofClass_array(request, sid):
    eleves_dic = {}
    classes_id = Classes.objects.filter(
        ecole_id=sid).values_list('id', flat=True)
    for classe_id in classes_id:
        eleves = Eleves.objects.filter(classe_id=classe_id)
        eleves_serializer = Eleves_serializer(eleves, many=True)
        eleves_data = eleves_serializer.data
        eleves_dict = eleves_data
        eleves_dic[classe_id] = eleves_dict
    return Response(eleves_dic)


@api_view(['GET'])
def get_working_profs(request, sid):
    profsDic = {}
    profs = Profs.objects.filter(ecole_id=sid).exclude(
        eid=0).order_by('-is_active', 'nom')
    prof_serializer = Profs_serializer(profs, many=True)
    for prof in prof_serializer.data:
        profsDic[prof['eid']] = prof
    return Response(profsDic)


@api_view(['GET'])
def get_profs_ofClass_array(request, sid):
    profs_dic = {}
    classes = Classes.objects.filter(ecole_id=sid).values_list('id', flat=True)
    for classe_id in classes:
        matieres = Matieres.objects.filter(classe_id=classe_id)
        matieres_serializer = Matiere_serializer(matieres, many=True)
        profs_dic[classe_id] = matieres_serializer.data
    return Response(profs_dic)


# @api_view(['GET'])
@api_view(['POST'])
def SaveElevesData(request, sid):
    try:
        AllEleves = request.data
        AllEleves_array = []
        for eleve in AllEleves:
            if (eleve["next_class"] != None and eleve["next_class"] != ""):
                eleve_model = Eleves(
                    id=eleve["id"], next_class_id=eleve["next_class"])
                AllEleves_array.append(eleve_model)
            else:
                eleve_model = Eleves(
                    id=eleve["id"], next_class_id=None)
                print("next_class = none or '' : "+str(eleve["id"]))
                AllEleves_array.append(eleve_model)
        if len(AllEleves_array) != 0:
            Eleves.objects.bulk_update(
                AllEleves_array, fields=['next_class'])
    except:
        return Response(False)
    return Response(True)


@api_view(['GET'])
def ResetElevesData(request, sid):
    try:
        AllelevesId = Eleves.objects.filter(
            ecole_id=sid).values_list('id', flat=True)
        Alleleves = []
        for eleve_id in AllelevesId:
            eleve = Eleves(id=eleve_id, next_class_id=None)
            Alleleves.append(eleve)
        Eleves.objects.bulk_update(Alleleves, fields=['next_class_id'])
    except:
        return Response(False)
    return Response(True)


####################################

@api_view(['POST'])
def add_new_class(request):
    if Classes.objects.filter(name=request.data["saisie_creat_classe"]).exists() != True:
        if add_class(dic["ecole_url"], request.data):
            return Response("class ajoute")
        else:
            return Response("mochkl")
    else:
        return Response("class name already exist")


@api_view(['POST'])
def del_class(request):  # add l isned 2 cuz l class has to have 0 students and 0 teachers in it
    class_to_del = Classes.objects.get(id=request.data["saisie_classe_supp"])
    print(class_to_del.count)
    if class_to_del.count == "0":
        bol = del__class(dic["ecole_url"], request.data)
        if bol:
            class_to_del.delete()
            return Response("class deleted")
        else:
            return Response("erreur")
    else:
        return Response("class not empty")
