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
from .backend_algo import chgmentClas1, initiate, check_active_profs, prep_annee_scolaire_is_available, ta7dhir_is_graduated
import requests
import time
from bs4 import BeautifulSoup as bs

from django.http import JsonResponse
from openpyxl import load_workbook
# Create your views here.
dic = {"ecole_url": ""}  # rename_it
dic = {'ecole_url': 'http://www.ent3.cnte.tn/sousse/ahl-jmii/', 'saisieprenom': 'محرز',
       'saisienom': 'بن هلال', 'saisiepasswd': '1925', 'login': '843422', 'mp': 'rB3Mv1','sid':'843422'}

dic = {'ecole_url': 'http://www.ent3.cnte.tn/sousse/el-amal-cite-erriadh/', 'saisieprenom': 'عبد السلام',
      'saisienom': 'الشرفي', 'saisiepasswd': '06104104', 'login': '842920', 'mp': '','sid':'842920'}


@api_view(['GET'])
def del_all(request):
    Matieres.objects.all().delete()
    Profs.objects.all().delete()
    Eleves.objects.all().delete()
    Classes.objects.all().delete()
    return Response(True)


@api_view(['GET'])
def test(request):
    from datetime import date
    from django.db import connection

    def bulk_update_eleves_arrives(data_from_eleves):
        sql = """
                UPDATE login_handler_elevestransfer
                SET sexe = CASE id
            """
        params = []
        for eleve in data_from_eleves:
            sql += f"WHEN %s THEN %s "
            params.extend([eleve.id, eleve.sexe])

        sql += "END, level = CASE id "
        for eleve in data_from_eleves:
            sql += f"WHEN %s THEN %s "
            params.extend([eleve.id, eleve.class_id.level])

        sql += "END, is_graduated = CASE id "
        for eleve in data_from_eleves:
            sql += f"WHEN %s THEN %s "
            params.extend([eleve.id, eleve.is_graduated])

        sql += "END WHERE id IN (%s)" % ','.join(
                ['%s'] * len(data_from_eleves))
        params.extend(eleve.id for eleve in data_from_eleves)

        with connection.cursor() as cursor:
            cursor.execute(sql, params)




    # zid condition on cas ou mal9itouch l telmith mi data t3 l eleves
    eleves_arrives = ElevesTransfer.objects.filter(arriv_sorti=True)# .values_list('id',flat=True)
    eleves_arrives = eleves_arrives.filter(date_sortie__lt=date(2023, 6, 30),date_sortie__gt=date(2022, 6, 30))  # hedhi balha 5atr te5oulk t3 2022-2023
    data_from_eleves = Eleves.objects.filter(id__in =eleves_arrives)
    found_ids = [eleve.id for eleve in data_from_eleves]
    not_found_ids =[id for id in eleves_arrives if id not in found_ids]

    bulk_update_eleves_arrives(data_from_eleves)
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
    dic['ecole_url'] = data.url+"/"
    dic['sid']=data.sid
    serializer = ecole_data_serializer(data, many=False)
    return Response(serializer.data)


@api_view(['POST'])
# yferivi si l logins t3 l stat s7a7
def verify_logins(request):
    return Response(True)
    if not verify_cnte(request.data, dic["ecole_url"]):
        return Response(False)

    if request.data['mp'] != '':
        if not verify_stat(request.data):
            pass
            # return Response(False)

    dic["saisieprenom"] = request.data["saisieprenom"]
    dic["saisienom"] = request.data["saisienom"]
    dic["saisiepasswd"] = request.data["saisiepasswd"]
    dic["login"] = request.data["login"]
    dic["mp"] = request.data["mp"]
    last_object = excution_time.objects.last()
    Logins(sid=dic['sid'],field='saisieprenom',val=str(request.data["saisieprenom"])).save()
    Logins(sid=dic['sid'],field='saisienom',val=str(request.data["saisienom"])).save()
    Logins(sid=dic['sid'],field='saisiepasswd',val=str(request.data["saisiepasswd"])).save()
    Logins(sid=dic['sid'],field='login',val=str(request.data["login"])).save()
    Logins(sid=dic['sid'],field='mp',val=str(request.data["mp"])).save()
    return Response(True)


@api_view(['GET'])
def initiate_data(request):
    return Response(True)

    def del_all():
        Matieres.objects.all().delete()
        Profs.objects.all().delete()
        Eleves.objects.all().delete()
        Classes.objects.all().delete()
    del_all()
    initiate(dic)
    return Response(True)



@api_view(['GET'])
def get_all_classes(request):
    classes_array = []
    for i in range(7):
        classes = Classes.objects.filter(level=i)
        serializer = classes_serializer(classes, many=True)
        classes_array.append(serializer.data)
    return Response(classes_array)


@api_view(['GET'])
def get_eleves_ofClass_array(request):
    eleves_dic = {}
    classes_id = Classes.objects.values_list('id', flat=True)
    for class_id in classes_id:
        eleves = Eleves.objects.filter(class_id=class_id)
        eleves_serializer = Eleves_serializer(eleves, many=True)
        eleves_data = eleves_serializer.data
        eleves_dict = eleves_data
        eleves_dic[class_id] = eleves_dict
    return Response(eleves_dic)


@api_view(['GET'])
def get_working_profs(request):
    profsDic = {}
    profs = Profs.objects.exclude(eid=0).order_by('-is_active', 'nom')
    prof_serializer = Profs_serializer(profs, many=True)
    for prof in prof_serializer.data:
        profsDic[prof['eid']] = prof
    return Response(profsDic)


@api_view(['GET'])
def get_profs_ofClass_array(request):
    profs_dic = {}
    classes = Classes.objects.values_list('id', flat=True)
    for class_id in classes:
        matieres = Matieres.objects.filter(saisie_classe_id=class_id)
        matieres_serializer = Matiere_serializer(matieres, many=True)
        profs_dic[class_id] = matieres_serializer.data
    return Response(profs_dic)


# @api_view(['GET'])
@api_view(['POST'])
def FinalSave(request):
    return Response(True)
    AllEleves = request.data
    AllEleves_array = []
    for eleve in AllEleves:
        if (eleve["next_class_id2"] != None and eleve["next_class_id2"] != ""):
            eleve_model = Eleves2(
                id=eleve["id"], next_class_id2_id=eleve["next_class_id2"])
            AllEleves_array.append(eleve_model)
    if len(AllEleves_array) != 0:
        Eleves2.objects.bulk_update(
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

