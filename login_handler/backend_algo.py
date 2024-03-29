import re
import time
from datetime import date
import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F, Value, Case, When, Q
from django.db.models.functions import Concat
from django.db.models import BooleanField
from django.db import transaction, connection

from .models import Classes, Ecole_data, Eleves, ElevesTransfer, Matieres, Matieres, Profs, Del1, Dre, excution_time, sexeEleves

from pprint import pprint


# ~ tnajjm tna7i al useless data like f m count
def class_ids(request, classes_dict, ecole_url: str):
    class_level = {"التحضيري": "0", "الأولى": "1", "الثانية": "2",
                   "الثالثة": "3", "الرابعة": "4", "الخامسة": "5", "السادسة": "6"}
    url = ecole_url+"consult_classe.php"
    response = request.get(url)
    soup = bs(response.text, 'html.parser')
    select_element = soup.find('select', {'id': 'saisie_classe'})
    classes_list = [i for i in select_element.children if i != '\n']
    for classe in classes_list[1:]:
        classe_id = classe['value'].strip()
        classe_niv_name = classe.text.strip()
        index = classe_niv_name.find(':')
        classe_niv = classe_niv_name[:index].replace(' ', '')
        classe_name = classe_niv_name[index+2:]
        classes_dict[classe_id] = [classe_name, class_level[classe_niv]]


def extract(request, classes_dict, eleve_dict, ecole_url: str):
    def is_valid_date_string(date_string):
        try:
            datetime.strptime(date_string, "%Y/%m/%d")
            return True
        except ValueError:
            return False

    url = ecole_url+"consult_classe.php"
    payload = {"saisie_classe": '', "consult": 'معاينة'}
    for class_id in classes_dict.keys():
        payload["saisie_classe"] = class_id
        response = request.post(url, data=payload)
        soup = bs(response.text, 'html.parser')
        table = soup.find('table', {'border': '1', "align": "center"})
        tr_s = [i for i in table.children if i != '\n']

        # eleves data
        if len(tr_s) > 2:   # m3neha l tableau fer8 walle
            for eleve in tr_s[2:]:
                eleve_data = [i for i in eleve.children if i != '\n']
                id = eleve_data[1].text.strip(
                ) if eleve_data[1].text.strip() != "" else None
                nom = eleve_data[2].text.strip()
                prenom = eleve_data[3].text.strip()
                sexe = eleve_data[4].text.strip()
                date_naissance = eleve_data[5].text.strip()
                date_naissance = date_naissance.replace(
                    '/', '-') if is_valid_date_string(date_naissance) else None
                eid_expression_string = str(eleve_data[7].input['onclick'])
                pattern = r"eid=(\d+)"
                match = re.search(pattern, eid_expression_string)
                eid = match.group(1)
                eleve_dict[eid] = [id, nom, prenom,
                                   sexe, date_naissance, class_id]


def insert_data_sql(classes_dict, eleve_dict, sid):
    print(eleve_dict)

    def alter_name(nom):
        nom = nom.replace('َ', '')  # fat7a
        nom = nom.replace('ً', '')  # fat7tin
        nom = nom.replace('ُ', '')  # dhama
        nom = nom.replace('ٌ', '')  # dhamtin
        nom = nom.replace('ُ', '')  # dhama
        nom = nom.replace('ِ', '')  # kasra
        nom = nom.replace('ٍ', '')  # zouz kasrat
        nom = nom.replace('ْ', '')  # soukoun
        nom = nom.replace('ـ', '')  # tajwid
        return nom

    class_objects = []
    for p, (name, level, ) in classes_dict.items():
        classe = Classes(
            cid=p,
            name=name,
            level=level,
            ecole_id=sid,
        )
        class_objects.append(classe)

    Classes.objects.bulk_create(class_objects)

    classes_ids = Classes.objects.filter(
        ecole_id=sid).values_list('cid', 'id')
    classes_ids_dic = {}
    for cid, id in classes_ids:
        classes_ids_dic[str(cid)] = str(id)

    eleve_objects = []
    male_eleves_array = []
    female_eleves_array = []

    for p, (uid, nom, prenom, sexe, date_naissance, classe_id) in eleve_dict.items():

        eleve = Eleves(
            eid=p,
            uid=uid,
            nom=nom,
            prenom=prenom,
            sexe=sexe,
            date_naissance=date_naissance,
            classe_id=classes_ids_dic[classe_id],
            ecole_id=sid,
        )
        eleve_objects.append(eleve)

        if sexe == 'ذكر':
            sexeeleve = sexeEleves(
                nom=alter_name(nom),
                male=True,
            )
            male_eleves_array.append(sexeeleve)
        elif sexe == 'أنثى':
            sexeeleve = sexeEleves(
                nom=alter_name(nom),
                female=True,
            )
            female_eleves_array.append(sexeeleve)

    with transaction.atomic():
        Eleves.objects.bulk_create(eleve_objects)
        sexeEleves.objects.bulk_create(
            male_eleves_array, ignore_conflicts=True)
        sexeEleves.objects.bulk_create(
            female_eleves_array, ignore_conflicts=True)
        sexeEleves.objects.bulk_update(male_eleves_array, fields=['male'],)
        sexeEleves.objects.bulk_update(female_eleves_array, fields=['female'])


# b4 callin it u ll wrap it in if statement cuz most likely it s not avaible if the annuelle_prep is already enabled
# n3rch chniya l cond bch t3ml 5atr idk yet prep annuel chisir ama chouf b3d l enable t3 l prep nrmlmnt yjik msg douba me tod5l l jadwl l ta9yimi zid 7ottou heka condition fil fonction hedhi just to be extra careful
def extract_moyen(request, ecole_url: str, sid):
    def custom_bulk_update_using_secondary_key(eleves_array):
        batch_size = 100  # Adjust this based on your database and performance testing

        # Generate SQL updates and parameters for each batch
        for batch_start in range(0, len(eleves_array), batch_size):
            batch_end = batch_start + batch_size
            batch_updates = eleves_array[batch_start:batch_end]
            # Construct the SQL update statement
            sql = """
                UPDATE login_handler_eleves
                SET moyen = CASE 
            """
            params = []
            for uid, float_moyen, resultat, is_graduated in batch_updates:
                sql += f"WHEN uid = %s AND ecole_id = %s THEN %s "
                params.extend([uid, sid, float_moyen])

            sql += "END, resultat = CASE "
            for uid, float_moyen, resultat, is_graduated in batch_updates:
                sql += f"WHEN uid = %s AND ecole_id = %s THEN %s "
                params.extend([uid, sid, resultat])

            sql += "END, is_graduated = CASE "
            for uid, float_moyen, resultat, is_graduated in batch_updates:
                sql += f"WHEN uid = %s AND ecole_id = %s THEN %s "
                params.extend([uid, sid, is_graduated])

            sql += "END WHERE uid IN (%s)" % ','.join(
                ['%s'] * len(batch_updates))
            params.extend(eleve_data[0] for eleve_data in batch_updates)

            # Execute the raw SQL update
            with connection.cursor() as cursor:
                cursor.execute(sql, params)

    def condition():    # a3ml condition
        return True

    if condition():
        url = ecole_url + 'pdf/pdf_recapfinal.php?id='
        classes = Classes.objects.filter(
            level__gt=0, ecole_id=sid).values_list('cid', flat=True)
        eleves_array = []
        for active_class in classes:
            url1 = url+str(active_class)
            response = request.get(url=url1)
            page = bs(response.text, 'html.parser')
            table = page.find('table', {'border': '1', 'dir': 'rtl'})
            # hedhi fil parsin l tr_s t3ha ytna7aw heka 3lh this one is this way
            td_s = [i for i in table.children if i != '\n']
            for i in range(1, len(td_s), 8):  # if u wonderin what is this look up
                id = td_s[i+1].text.strip()
                moyen = td_s[i+5].text.strip()
                float_moyen = float(moyen) if moyen != '' else None
                resultat = td_s[i+7].text.strip()
                is_graduated = None
                if 'يرتقي' in resultat:
                    is_graduated = True
                elif resultat == 'يرسب':
                    is_graduated = False
                else:
                    is_graduated = None
                    resultat = None
                if id != "":
                    eleves_array.append(
                        (id, float_moyen, resultat, is_graduated))
                else:
                    nom_prenom = td_s[i].text.strip()
                    eleve = Eleves.objects.annotate(full_name_concat=Concat(F('nom'), Value(' '), F('prenom'))
                                                    ).filter(full_name_concat__iexact=nom_prenom, uid=None, ecole_id=sid)
                    if eleve:
                        eleve.update(
                            moyen=float_moyen, resultat=resultat, is_graduated=is_graduated)
                    else:
                        print(nom_prenom + ' not found id = none')

        custom_bulk_update_using_secondary_key(eleves_array)

    else:
        def eleves_racha_age():
            year = 2013  # yzid yn9os kol 3al maybe a3melou algo for that
            for i in range(1, 7):
                classes_ofLevel = Classes.objects.filter(
                    level=i, ecole_id=sid).values_list('id', flat=True)
                old_eleves_lt10 = Eleves.objects.filter(classe_id__in=classes_ofLevel).filter(
                    date_naissance__lt=date(year, 7, 16), moyen__lt=10)
                old_eleves_lt10.update(
                    is_graduated=True, resultat='يرتقي بالإسعاف العمري')
                year -= 1

        url = ecole_url+"liste_distribution.php"
        payload = {
            "niveau": "",
            "inf": "0",
            "supp": "20",
            "liste": "ابعث",
        }
        eleves_array = []
        for i in range(1, 7):
            payload["niveau"] = str(i)
            response = request.post(url, data=payload)
            soup = bs(response.content.decode(
                encoding='utf-8', errors='ignore'), 'html.parser')
            table = soup.find("table", {"id": "datatables"}).tbody
            tr_s = [i for i in table.children if i != '\n']

            for eleve in tr_s:
                eleve_data = [i for i in eleve.children if i != '\n']
                eleve_id = eleve_data[2].text.strip()
                moyen = eleve_data[5].text.strip()
                if eleve_id != '':
                    moyen_float = float(moyen) if moyen != '' else None
                    resultat = None
                    is_graduated = None
                    if moyen_float >= 10:
                        resultat = 'يرتقي'
                        is_graduated = True
                    elif moyen_float < 9:
                        resultat = 'يرسب'
                        is_graduated = False
                    else:
                        resultat = None
                        is_graduated = None
                    eleves_array.append(
                        (eleve_id, moyen_float, resultat, is_graduated))
                else:
                    nom_prenom = eleve_data[1].text.strip()
                    eleve = Eleves.objects.annotate(full_name_concat=Concat(F('nom'), Value('  '), F('prenom'))
                                                    ).filter(full_name_concat__iexact=nom_prenom, uid=None, ecole_id=sid)
                    if eleve:
                        is_graduated = None
                        resultat = None
                        if moyen_float >= 10:
                            is_graduated = True
                            resultat = 'يرتقي'
                        elif moyen_float < 9:
                            is_graduated = False
                            resultat = 'يرسب'
                        eleve.update(
                            moyen=moyen_float, resultat=resultat, is_graduated=is_graduated)
                    else:
                        print(nom_prenom + ' not found id = none')

        custom_bulk_update_using_secondary_key(eleves_array)
        eleves_racha_age()


# 9a3d te5ou fil info l kol meme ci 9a3d test3ml ken fil eid nom prenom chouf ken 7achtk bihom sinn let them go
def prof_data(request, ecole_url, sid):
    url = ecole_url+"list_enseignant.php"
    response = request.get(url)
    soup = bs(response.text, 'html.parser')
    table = soup.find('form').table
    profs_array = []

    for prof_data in table.findChildren("tr", {"class": "tabnormal2"}):
        prof_data_list = [i for i in prof_data.children if i != '\n']
        prof_name = prof_data_list[1].text.strip()
        prof_prenom = prof_data_list[2].text.strip()
        prof_id_manuel = prof_data_list[4].text.strip()
        prof_id_ministre = prof_data_list[5].text.strip()
        prof_eid = prof_data_list[6].input['onclick']
        index_start = prof_eid.find('id=')+3
        index_finish = prof_eid.find('&verif')
        prof_eid = prof_eid[index_start: index_finish]
        prof = Profs(
            eid=prof_eid,
            nom=prof_name,
            prenom=prof_prenom,
            pid=prof_id_ministre if prof_id_ministre != '' else None,
            ecole_id=sid
        )
        profs_array.append(prof)
    with transaction.atomic():
        Profs.objects.bulk_create(profs_array)


# look if this one still available after prep annee
def check_active_classes(request, ecole_url: str, sid):
    url = ecole_url+"modifaffect.php"
    response = request.get(url=url)
    soup = bs(response.text, 'html.parser')

    tr_table = soup.find('tr', {"id": 'cadreCentral0'})

    trs = tr_table.findAll('tr', {"class": 'tabnormal2'})

    classes_dic = {}
    classes = Classes.objects.filter(ecole_id=sid).values_list('name', 'id')
    for name, id in classes:
        classes_dic[name] = id
    classes = []
    for tr in trs:
        classe_name = tr.td.text.strip()
        classe = Classes(id=classes_dic[classe_name], is_active=True)
        classes.append(classe)
    Classes.objects.bulk_update(classes, fields=['is_active'])


# ~works but u didnt give it 100% check minors conditions or somen
def matieres(request, ecole_url, sid):
    def createprof0():  # just in case l matiere fihch prof
        prof0 = Profs(eid=0)
        prof0.nom = ""
        prof0.prenom = ""
        prof0.ecole = Ecole_data.objects.get(sid=sid)
        prof0.save()
    createprof0()

    profs_ = Profs.objects.filter(ecole_id=sid).values_list('eid', 'id')
    profs_ids = {}
    for eid, id in profs_:
        profs_ids[str(eid)] = id
    matieres_array = []

    def create_matiere(classe, field_name, prof_id):
        matiere = Matieres(
            field=field_name,
            classe=classe,
            prof_id=prof_id,
            ecole_id=sid,
        )
        matieres_array.append(matiere)

    def add_matieres(classe, level, matieres_dic):
        prof_id_arab = matieres_dic["مجال اللغة العربية التواصل الشفوي و المحفوظات"]
        create_matiere(classe, "arab", profs_ids[prof_id_arab])

        prof_id_math = matieres_dic["مجال العلوم و التكنولوجيا الرياضيات"]
        create_matiere(classe, "math", profs_ids[prof_id_math])

        prof_id_science = matieres_dic["مجال العلوم و التكنولوجيا الايقاظ العلمي"]
        create_matiere(classe, "science", profs_ids[prof_id_science])

        prof_id_technique = matieres_dic["مجال العلوم و التكنولوجيا التربية التكنولوجية"]
        create_matiere(classe, "technique", profs_ids[prof_id_technique])

        prof_id_islam = matieres_dic["مجال التنشئة التربية الاسلامية"]
        create_matiere(classe, "islam", profs_ids[prof_id_islam])

        if level >= "5":
            prof_id_histoiregeo = matieres_dic["مجال التنشئة التاريخ"]
            create_matiere(classe, "histoiregeo",
                           profs_ids[prof_id_histoiregeo])

        prof_id_draw = matieres_dic["مجال التنشئة التربية التشكيلية"]
        create_matiere(classe, "draw", profs_ids[prof_id_draw])

        prof_id_music = matieres_dic["مجال التنشئة التربية الموسيقية"]
        create_matiere(classe, "music", profs_ids[prof_id_music])

        prof_id_sport = matieres_dic["مجال التنشئة التربية البدنية"]
        create_matiere(classe, "sport", profs_ids[prof_id_sport])

        if level >= "2":
            prof_id_francais = matieres_dic["مجال اللغة الفرنسية Exp. Orale Et Recitation"]
            create_matiere(classe, "francais", profs_ids[prof_id_francais])

        if level >= "4":
            prof_id_anglais = matieres_dic["مجال اللغة الانجليزية اللغة الانجليزية"]
            create_matiere(classe, "anglais", profs_ids[prof_id_anglais])

    active_classes = Classes.objects.filter(is_active=True, ecole_id=sid)
    url = ecole_url+"modifaffect2.php?saisie_classe_envoi="
    payload = {"saisie_classe_envoi": ""}
    for active_class in active_classes:
        matieres_dic = {}
        payload["saisie_classe_envoi"] = str(active_class.cid)
        response = request.get(url=url+str(active_class.cid), data=payload)
        soup = bs(response.content.decode(
            encoding='utf-8', errors='ignore'), 'html.parser')
        tr_table = soup.find('tr', {"id": 'cadreCentral0'})
        trs = tr_table.td.table.tr.td.table
        trs_list = [i for i in trs.findChildren('tr')]
        for tr in trs_list[1:]:
            tds = [i for i in tr.children if i != '\n']
            prof_eid = tds[2].find('select').option['value'].strip()
            nom_matiere = tds[1].find('select').option.text.strip()
            matieres_dic[nom_matiere] = prof_eid
        add_matieres(active_class, active_class.level, matieres_dic)

    inactive_classes = Classes.objects.filter(is_active=False, ecole_id=sid)
    for inactive_class in inactive_classes:
        matieres_dic = {
            "مجال اللغة العربية التواصل الشفوي و المحفوظات": "0",
            "مجال العلوم و التكنولوجيا الرياضيات": "0",
            "مجال العلوم و التكنولوجيا الايقاظ العلمي": "0",
            "مجال العلوم و التكنولوجيا التربية التكنولوجية": "0",
            "مجال التنشئة التربية الاسلامية": "0",
            "مجال التنشئة التاريخ": "0",
            "مجال التنشئة التربية التشكيلية": "0",
            "مجال التنشئة التربية الموسيقية": "0",
            "مجال التنشئة التربية البدنية": "0",
            "مجال اللغة الفرنسية Exp. Orale Et Recitation": "0",
            "مجال اللغة الانجليزية اللغة الانجليزية": "0",
        }
        add_matieres(inactive_class, inactive_class.level, matieres_dic)
    with transaction.atomic():
        Matieres.objects.bulk_create(matieres_array)


def check_active_profs(sid):

    sql = """
    UPDATE login_handler_profs
    SET is_active = 1
    WHERE id IN (
        SELECT DISTINCT prof_id
        FROM (
            SELECT prof.id AS prof_id
            FROM login_handler_profs AS prof
            JOIN login_handler_matieres AS matiere ON prof.id = matiere.prof_id
            WHERE matiere.ecole_id = %s
        ) AS subquery
    );
    """

    # Execute the SQL query
    with connection.cursor() as cursor:
        cursor.execute(sql, [sid])


def preparatoire_is_graduated(sid):
    prep_classes_id = Classes.objects.filter(
        level='0', ecole_id=sid).values_list('id', flat=True)
    prep_eleves = Eleves.objects.filter(classe_id__in=prep_classes_id)
    for eleve in prep_eleves:
        eleve.is_graduated = True

    Eleves.objects.bulk_update(prep_eleves, fields=['is_graduated'])


def initiate(dic):
    request = requests.session()
    classes_dict = {}
    eleve_dict = {}
    url = dic['ecole_url'] + "acces.php"
    payload = {"saisieprenom": dic["saisieprenom"],
               "saisienom": dic["saisienom"],
               "saisiepasswd": dic["saisiepasswd"],
               "saisie_membre": "administrateur",
               }

    request.post(url=url, data=payload)

    # --------------
    last_object = excution_time.objects.last()
    new_id2 = last_object.id2 + 1

    first_start_time = time.time()
    class_ids(request, classes_dict, dic['ecole_url'])
    end_time = time.time()
    execution_time = end_time - first_start_time
    excution_time(id2=new_id2, funct='class_ids',
                  time=str(execution_time)).save()

    start_time = time.time()
    extract(request, classes_dict, eleve_dict, dic['ecole_url'])
    end_time = time.time()
    execution_time = end_time - start_time
    excution_time(id2=new_id2, funct='extract',
                  time=str(execution_time)).save()

    start_time = time.time()
    insert_data_sql(classes_dict, eleve_dict, dic['sid'])
    preparatoire_is_graduated(dic['sid'])
    end_time = time.time()
    execution_time = end_time - start_time
    excution_time(id2=new_id2, funct='insert_data_sql',
                  time=str(execution_time)).save()

    start_time = time.time()
    if prep_annee_scolaire_is_available(dic['ecole_url']):
        extract_moyen(request, dic['ecole_url'], dic['sid'])
    else:
        extract_moyen_from_archive(request, dic['ecole_url'], dic['sid'])
    end_time = time.time()
    execution_time = end_time - start_time
    excution_time(id2=new_id2, funct='extract_moyen',
                  time=str(execution_time)).save()

    start_time = time.time()
    prof_data(request, dic['ecole_url'], dic['sid'])
    end_time = time.time()
    execution_time = end_time - start_time
    excution_time(id2=new_id2, funct='prof_data',
                  time=str(execution_time)).save()

    start_time = time.time()
    # ~ do u rlly need it ? ,
    check_active_classes(request, dic['ecole_url'], dic['sid'])
    end_time = time.time()
    execution_time = end_time - start_time
    excution_time(id2=new_id2, funct='check_active_classes',
                  time=str(execution_time)).save()

    start_time = time.time()
    matieres(request, dic['ecole_url'], dic['sid'])
    end_time = time.time()
    execution_time = end_time - start_time
    excution_time(id2=new_id2, funct='matieres',
                  time=str(execution_time)).save()

    start_time = time.time()
    check_active_profs(dic['sid'])
    end_time = time.time()
    execution_time = end_time - start_time
    excution_time(id2=new_id2, funct='check_active_profs',
                  time=str(execution_time)).save()

    start_time = time.time()
    Eleves_arrives_sorties(request, dic['ecole_url'], dic['sid'])
    end_time = time.time()
    execution_time = end_time - start_time
    excution_time(id2=new_id2, funct='Eleves_arrives_sorties',
                  time=str(execution_time)).save()

    start_time = time.time()
    Eleves_arrives_sexe_class(dic['sid'])
    end_time = time.time()
    execution_time = end_time - start_time
    excution_time(id2=new_id2, funct='Eleves_arrives_sexe_class',
                  time=str(execution_time)).save()

    execution_time = end_time - first_start_time
    excution_time(id2=new_id2, funct='all', time=str(execution_time)).save()
    excution_time(id2=new_id2, funct='', time='').save()
    request.close()


# ken prep_annee_scolaire_is_available is false
# ~ na7i l case ki zibbi wel bulk update too
def extract_moyen_from_archive(request, ecole_url: str, sid):
    def eleves_racha_age():
        year = 2013  # yzid yn9os kol 3al maybe a3melou algo for that
        for i in range(1, 7):
            classes_ofLevel = Classes.objects.filter(
                level=i, ecole_id=sid).values_list('id', flat=True)
            old_eleves_lt10 = Eleves.objects.filter(classe_id__in=classes_ofLevel, ecole_id=sid).filter(
                date_naissance__lt=date(year, 7, 16), moyen__lt=10)
            old_eleves_lt10.update(
                is_graduated=True, resultat='يرتقي بالإسعاف العمري')
            year -= 1

    url = ecole_url + "imprime_ancien1.php"
    payload = {"annee_s": "2021-2022"}   # baddl l 3am hedha t3 wilt 3ambewil
    response = request.post(url, data=payload)
    soup = bs(response.text, 'html.parser')
    table = soup.find('table', {'id': 'datatables'}).tbody
    eleves_urls = list(table.find_all('a'))
    urls = []
    for eleve_url in eleves_urls:
        try:
            if eleve_url['href'].find('visu_bulletin_finaleleve') != -1:
                urls.append(eleve_url['href'])
        except:
            print("error extract_moyen_from_archive : "+eleve_url)
    existing_students = Eleves.objects.filter(
        ecole_id=sid).values_list('eid', 'id')
    pks_dic = {}
    for eid, id in existing_students:
        pks_dic[eid] = id

    def del_old_eid(url):
        index1 = url.find("idelev=")
        index2 = url[index1:].find("&")
        eid = int(url[index1+7:index1+index2])
        return eid in pks_dic.keys()

    filtered_urls = [url for url in urls if del_old_eid(url)]

    eleves_to_update = []
    for bulltin_url in filtered_urls:
        url = ecole_url+bulltin_url
        response = request.get(url)
        soup = bs(response.text, 'html.parser')

        moyen_tag = soup.find('td', {
                              'align': 'center', 'style': 'border: 1px solid #9BCDFF; padding-left: 4px; padding-right: 4px; padding-top: 1px; padding-bottom: 1px', 'width': '35%'})
        moyen = moyen_tag.text if moyen_tag else ""

        resultat_tag = soup.find('font', {'size': '6'})
        resultat = resultat_tag.text if resultat_tag else ""

        name_tag = soup.find(
            'td', {'dir': 'rtl', 'width': '224', "colspan": "2", 'height': "21"})
        # ism l telmidh just in case if u want to later
        name = name_tag.text if name_tag else ""

        index1 = url.find("idelev=")
        index2 = url[index1:].find("&")
        eid = int(url[index1+7:index1+index2])

        moyen_float = float(moyen.replace(',', '.'))

        case_expression = Case(
            When(resultat__icontains="يرتقي", then=True),
            When(resultat__icontains="يرسب", then=False),
            When(moyen__gte=10, then=True),
            When(moyen__lt=9, then=False),
            default=None,
            output_field=BooleanField()
        )

        eleve = Eleves(id=pks_dic[eid], moyen=moyen_float, resultat=resultat,
                       is_graduated=case_expression)
        eleves_to_update.append(eleve)

    Eleves.objects.bulk_update(eleves_to_update, fields=[
        'moyen', 'resultat', 'is_graduated'])
    eleves_racha_age()


# check  تحضير السنة الدراسية manzoul 3leha walle
# laktheriya bch tbadlha
def prep_annee_scolaire_is_available(ecole_url: str):
    return True
    url = ecole_url+"newannee.php"
    response = request.get(url)
    if response.text.find("لقد قمتم  بتحضير السنة الدراسية سابقاً بنجاح") != -1:
        print("String found!")
    else:
        print("String not found.")


def Eleves_arrives_sorties(request, ecole_url: str, sid):
    def is_valid_date_string(date_string):
        try:
            datetime.strptime(date_string, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def code(url, arriv_sorti_bool):
        response = request.get(url)
        soup = bs(response.text, 'html.parser')
        table = soup.find("table", {"id": "datatables"}).tbody
        tr_s = [i for i in table.children if i != '\n']

        ElevesTransfer_array = []

        for eleve in tr_s:
            eleve_data = [i for i in eleve.children if i != '\n']
            eleve_id = eleve_data[0].text.strip()
            eleve_nom = eleve_data[1].text.strip()
            eleve_prenom = eleve_data[2].text.strip()
            prev_ecole = eleve_data[3].text.strip()
            date_naissance = eleve_data[4].text.strip()
            date_naissance = date_naissance if is_valid_date_string(
                date_naissance) else None
            date_sortie = eleve_data[5].text.strip()
            date_sortie = date_sortie if is_valid_date_string(
                date_naissance) else None
            eleve_object = ElevesTransfer(
                uid=(eleve_id if eleve_id != "" else None),
                nom=eleve_nom,
                prenom=eleve_prenom,
                prev_new_ecole=prev_ecole,
                date_naissance=date_naissance,
                date_sortie=date_sortie,
                arriv_sorti=arriv_sorti_bool,
                ecole_id=sid
            )
            ElevesTransfer_array.append(eleve_object)
        with transaction.atomic():
            ElevesTransfer.objects.bulk_create(ElevesTransfer_array)

    ElevesTransfer.objects.all().delete()  # ~
    url = ecole_url + 'eleve_arrivees.php'
    code(url, True)
    url = ecole_url + 'eleves_abondans.php'
    code(url, False)


def Eleves_arrives_sexe_class(sid):

    def bulk_update_eleves_arrives(data_from_eleves):
        sql = """
                UPDATE login_handler_elevestransfer
                SET sexe = CASE 
            """
        params = []
        for eleve in data_from_eleves:
            sql += f"WHEN uid = %s AND ecole_id = %s THEN %s "
            params.extend([eleve.uid, sid, eleve.sexe])

        sql += "END, level = CASE  "
        for eleve in data_from_eleves:
            sql += f"WHEN uid = %s AND ecole_id = %s THEN %s "
            params.extend([eleve.uid, sid, eleve.classe.level])

        sql += "END, is_graduated = CASE  "
        for eleve in data_from_eleves:
            sql += f"WHEN uid = %s AND ecole_id = %s THEN %s "
            params.extend([eleve.uid, sid, eleve.is_graduated])

        sql += "END WHERE uid IN (%s)" % ','.join(
            ['%s'] * len(data_from_eleves))
        params.extend(eleve.uid for eleve in data_from_eleves)

        with connection.cursor() as cursor:
            cursor.execute(sql, params)

    # zid condition lil not_found_ids t3 tlemtha l mehomch fil madrsa (they can be in  بقية التلاميذ المسجلين عن بعد ama mezelch me7athomch f class yet )
    eleves_arrives = ElevesTransfer.objects.filter(
        arriv_sorti=True, ecole_id=sid)  # .values_list('id',flat=True)
    eleves_arrives = eleves_arrives.filter(date_sortie__gt=date(
        2022, 6, 30), date_sortie__lt=date(2023, 6, 30)).values_list('uid', flat=True)  # hedhi balha 5atr te5oulk t3 2022-2023
    # ~ hedhi ken bdet fer8a dhahrli t3ml error l func bulk_update_eleves_arrives dhabt w3ml cond
    data_from_eleves = Eleves.objects.filter(
        uid__in=eleves_arrives, ecole_id=sid)
    found_ids = [eleve.uid for eleve in data_from_eleves]
    not_found_ids = [id for id in eleves_arrives if id not in found_ids]

    bulk_update_eleves_arrives(
        data_from_eleves) if data_from_eleves.exists() else None


##############################
def chgmentClas1(ecole_url: str):
    url = ecole_url + 'chgmentClas1.php'
    sorted_classes = Classes.objects.all().order_by('-level', 'name')
    for classe in sorted_classes:
        inceremnt = 0
        payload = {"idEleve[]": [], "new_classe[]": [],
                   "rien": "ابعث  التغييرات", "nbEleve": ""}
        elevsClass = Eleves.objects.filter(class_id=classe)
        for eleve in elevsClass:
            inceremnt += 1
            eid = eleve.eid
            if (eleve.next_class == None or eleve.next_class == eleve.classe):
                nxt_class = "rien"
            else:
                nxt_class = eleve.next_class.id
            payload["idEleve[]"].append(str(eid))
            payload["new_classe[]"].append(str(nxt_class))
        payload["nbEleve"] = str(inceremnt)
        print(payload)
    print(url)


# yzid l id t3 l wileya wel mo3tamdiya lil ecole_data
def update_dre_del1():  # ~ chouf ken tnajjmch tzid t7assn fih bidou w ki kamltou r9dt w 8odwa u just went out of the flow of the algo
    Dre.objects.all().delete()
    Del1.objects.all().delete()
    request = requests.session()
    url = "http://stat.education.tn/index.php"
    payload = {"login": "843422", "mp": "rB3Mv1"}

    page = request.post(url=url, data=payload)

    # wileya
    url = "http://stat.education.tn/deplacement_etudiants/src/prim/depuis/eleve.php?code_etab=843422&choix_annee=2022&del_etab=8434&dre_etab=84&type_etab=10"
    response = request.get(url, data=payload)
    page = bs(response.text, 'html.parser')
    data = page.find('select', {'id': 'dre'})
    options = [i for i in data.children if i != '\n']
    dre_array = []
    del1_array = []
    dre_id_and_stat_school_name_array = []
    ecole_data_del1_array = []
    for option in options[1:]:
        name = option.text.strip()
        name = name.replace('المندوبية الجهوية للتربية بـ', '')
        name = name.replace('المندوبية الجهوية بـ', '')
        name = name.replace('المندوبية الجهوية ب', '')
        dre_id = option["value"]
        if dre_id.isdigit():
            dre_object = Dre(id=dre_id, name=name)
            dre_array.append(dre_object)

            # mo3tamdiya
            url = "http://stat.education.tn/deplacement_etudiants/src/prim/depuis/delegation.php?dre="+dre_id
            response = request.get(url)
            page = bs(response.text, 'html.parser')
            data = page.find('select', {'id': 'del'})
            options = [i for i in data.children if i != '\n']
            for option in options[1:]:

                name = option.text.strip()
                val = option["value"]
                if val.isdigit():
                    del1_object = Del1(id=val, name=name)
                    del1_array.append(del1_object)

                    matching_sids = list(Ecole_data.objects.filter(
                        sid__startswith=val).values_list('sid', flat=True))
                    for sid in matching_sids:
                        ecole_data_del1_object = Ecole_data(sid=sid)
                        ecole_data_del1_array.append(ecole_data_del1_object)

            # mederes   # hedhi tnajjm tna7eha ama thabt se3a l info l te5ou feha useless cuz bascically u only takin the snd name cohuf ken fil search 3al tlemdha l monta9lin wel jeyin est que uselfull sinn zeyd
            url = "http://stat.education.tn/deplacement_etudiants/src/prim/depuis/etablissement.php?dre="+dre_id
            response = request.get(url)
            page = bs(response.text, 'html.parser')
            data = page.find('select', {'id': 'etab'})
            options = [i for i in data.children if i != '\n']
            for option in options[1:]:
                name = option.text.strip()
                val = option["value"]
                if val.isdigit():
                    sid = int(val)
                    stat_school_name_object = Ecole_data(
                        sid=sid, stat_school_name=name)
                    dre_id_and_stat_school_name_array.append(
                        stat_school_name_object)

    with transaction.atomic():
        Dre.objects.bulk_create(dre_array)
        Del1.objects.bulk_create(del1_array)
        Ecole_data.objects.bulk_update(
            dre_id_and_stat_school_name_array, fields=['stat_school_name'])

    dre_ids = Dre.objects.values_list('id', flat=True)
    ecole_objects = []
    for dre_id in dre_ids:
        sids = Ecole_data.objects.filter(
            sid__startswith=dre_id).values_list('sid', flat=True)
        for sid in sids:
            ecole_objects.append(Ecole_data(sid=sid, dre_id=dre_id))
    Ecole_data.objects.bulk_update(ecole_objects, fields=['dre_id'])

    del1_ids = Del1.objects.values_list('id', flat=True)
    ecole_objects = []
    for del1_id in del1_ids:
        sids = Ecole_data.objects.filter(
            sid__startswith=del1_id).values_list('sid', flat=True)
        for sid in sids:
            ecole_objects.append(Ecole_data(sid=sid, del1_id=del1_id))
    Ecole_data.objects.bulk_update(ecole_objects, fields=['del1_id'])


def nbr_elevs_schools():
    dic = {'ecole_url': 'http://www.ent3.cnte.tn/sousse/ahl-jmii/', 'saisieprenom': 'محرز',
           'saisienom': 'بن هلال', 'saisiepasswd': '1925', 'login': '843422', 'mp': 'rB3Mv1', 'sid': '843422'}
    url = dic['ecole_url'] + "acces.php"
    payload = {"saisieprenom": dic["saisieprenom"],
               "saisienom": dic["saisienom"],
               "saisiepasswd": dic["saisiepasswd"],
               "saisie_membre": "administrateur",
               }

    request = requests.session()
    request.post(url=url, data=payload)
    url = "http://www.ent.cnte.tn/stat/ecolepartiel.php?par=843422"
    response = request.get(url=url)
    page = bs(response.text, 'html.parser')
    select_element = page.find('select',{'name':'gouv'})
    gouvs_names = [i for i in select_element.children if i!='\n']
    gouvs=[]
    for gouv in gouvs_names[1:]:
        gouv_name = gouv['value']
        gouvs.append(gouv_name)
    
    for gouv in gouvs:
        payload = {
        'gouv': gouv,
        'ecole': 'rien',
        }
        response = request.post(url=url,data=payload )
        page = bs(response.text, 'html.parser')
        select_element = page.find('select', {'name': 'ecole'})
        options = [i for i in select_element.children if i != '\n']
        ls = []
        for option in options[1:]:
            text = option['value']
            first_etoile = text.find("*")
            sid = text[0:first_etoile]
            second_etoile = text.find("*", text.find("*") + 1)
            third_etoile = text.find("*", second_etoile + 1)
            nbr = text[second_etoile+1:third_etoile]
            data = Ecole_data(sid=sid, nbr_elev=nbr)
            ls.append(data)
        Ecole_data.objects.bulk_update(ls, fields=['nbr_elev'])


#######################################

def other():    # ~ 5arrjt mnha l loop l fi site tall3t beha l id t3 classet w notet l tlemtha
    url = 'http://www.ent3.cnte.tn/sousse/sahloul/pdf/pdf_recapfinal.php?id='
    request = requests.session()
    for i in range(0, 100):
        url1 = url+str(i)
        response = request.get(url=url1)
        page = bs(response.text, 'html.parser')
        table = page.find('table', {'border': '1', 'dir': 'rtl'})
        # hedhi fil parsin l tr_s t3ha ytna7aw heka 3lh this one is this way
        td_s = [i for i in table.children if i != '\n']
        if len(td_s) > 1:
            print('wowowowow : '+str(i))
        else:
            print('non : '+str(i))





