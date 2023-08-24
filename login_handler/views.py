import pprint
from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F, Value
from django.db.models.functions import Concat
from django.db import transaction

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Ecole_data, Eleves, Classes, ElevesTransfer, Matieres, Matieres, Profs, Logins, Del1, Dre, sexeEleves
from .serializers import Eleves_serializer, Matiere_serializer, Profs_serializer, classes_serializer, ecole_data_serializer
from .views_subfunct import del__class, verify_cnte, verify_stat, add_class
from .backend_algo import chgmentClas1, initiate
import requests
import time
from bs4 import BeautifulSoup as bs

from django.http import JsonResponse
from openpyxl import load_workbook
# Create your views here.

dic = {'ecole_url': 'http://www.ent3.cnte.tn/sousse/ahl-jmii/', 'saisieprenom': 'محرز',
       'saisienom': 'بن هلال', 'saisiepasswd': '1925', 'login': '843422', 'mp': 'rB3Mv1', 'sid': '843422'}

#dic = {'ecole_url': 'http://www.ent3.cnte.tn/sousse/el-amal-cite-erriadh/', 'saisieprenom': 'عبد السلام',
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
    url ='http://www.ent3.cnte.tn/sousse/sahloul/pdf/pdf_recapfinal.php?id='
    request = requests.session()
    for i in range(0,100):
        url1 = url+str(i)
        response = request.get(url=url1)
        page = bs(response.text, 'html.parser')
        table = page.find('table', {'border': '1', 'dir': 'rtl'})
        # hedhi fil parsin l tr_s t3ha ytna7aw heka 3lh this one is this way
        td_s = [i for i in table.children if i != '\n']
        if len(td_s)>1:
            print('wowowowow : '+str(i))
        else:
            print('non : '+str(i))

    
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


@api_view(['POST'])
def initiate_data(request):
    #return Response(True)
    def del_all():
        #Matieres.objects.all().delete()
        #Profs.objects.all().delete()
        #Eleves.objects.all().delete()
        #Classes.objects.all().delete()
        pass
    del_all()

    initiate(request.data)
    return Response(True)
    #initiate(dic)



@api_view(['GET'])
def initiate_data_to_fronent(request):
    return Response(True)


@api_view(['GET'])
def get_all_classes(request,sid):
    classes_array = []
    for i in range(7):
        classes = Classes.objects.filter(level=i,ecole_id=sid)
        serializer = classes_serializer(classes, many=True)
        classes_array.append(serializer.data)
    return Response(classes_array)


@api_view(['GET'])
def get_eleves_ofClass_array(request,sid):
    eleves_dic = {}
    classes_id = Classes.objects.filter(ecole_id=sid).values_list('id', flat=True)
    for classe_id in classes_id:
        eleves = Eleves.objects.filter(classe_id=classe_id)
        eleves_serializer = Eleves_serializer(eleves, many=True)
        eleves_data = eleves_serializer.data
        eleves_dict = eleves_data
        eleves_dic[classe_id] = eleves_dict
    return Response(eleves_dic)


@api_view(['GET'])
def get_working_profs(request,sid):
    profsDic = {}
    profs = Profs.objects.filter(ecole_id=sid).exclude(eid=0).order_by('-is_active', 'nom')
    prof_serializer = Profs_serializer(profs, many=True)
    for prof in prof_serializer.data:
        profsDic[prof['eid']] = prof
    return Response(profsDic)


@api_view(['GET'])
def get_profs_ofClass_array(request,sid):
    profs_dic = {}
    classes = Classes.objects.filter(ecole_id=sid).values_list('id', flat=True)
    for classe_id in classes:
        matieres = Matieres.objects.filter(classe_id=classe_id)
        matieres_serializer = Matiere_serializer(matieres, many=True)
        profs_dic[classe_id] = matieres_serializer.data
    return Response(profs_dic)


# @api_view(['GET'])
@api_view(['POST'])
def FinalSave(request):
    return Response(True)
    AllEleves = request.data
    AllEleves_array = []
    for eleve in AllEleves:
        if (eleve["next_class_id2"] != None and eleve["next_class_id2"] != ""):
            eleve_model = Eleves(
                id=eleve["id"], next_class_id2_id=eleve["next_class_id2"])
            AllEleves_array.append(eleve_model)
    if len(AllEleves_array) != 0:
        Eleves.objects.bulk_update(
            AllEleves_array, fields=['next_class_id2_id'])
        chgmentClas1(dic['ecole_url'])
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
