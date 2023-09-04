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

from login_handler.backend_algo import class_ids, extract

from .models import Classes, Ecole_data, Eleves, ElevesTransfer, Matieres, Matieres, Profs, Del1, Dre, excution_time, sexeEleves

from pprint import pprint


def compare(classes_dict: dict, eleve_dict: dict, sid):
    #0 add new classes and updates classes names , not deletion for old classes
    
    uptodate_cids =set(classes_dict.keys())
    int_database_cid = Classes.objects.filter(ecole_id=sid).values_list('cid',flat=True)
    str_database_cid = set(str(cid) for cid in int_database_cid)
    deleted_classes = str_database_cid-uptodate_cids

    
    for cid in uptodate_cids:
        if int(cid) not in int_database_cid:
            classe = classes_dict[cid]
            print('zed class : '+ classe[0])
            Classes(
                cid=cid,
                name=classe[0],
                level=classe[1],
                ecole_id=sid,
                ).save()

    def bulk_update_classes(classes_dict,uptodate_cids):
        sql = """
                UPDATE login_handler_classes
                SET name = CASE 
            """
        params = []
        for cid in uptodate_cids:
            sql += f"WHEN cid = %s THEN %s "
            params.extend([cid,classes_dict[cid][0]])
            
        sql += "END WHERE ecole_id= %s "
        params.append(sid)

        sql += "AND cid IN (%s)" % ','.join(
            ['%s'] * len(uptodate_cids))
        params.extend(cid for cid in uptodate_cids)

        with connection.cursor() as cursor:
            cursor.execute(sql, params)

    bulk_update_classes(classes_dict,uptodate_cids)


    #1 removing eleves_sorties
 #   uptodate_eid =list(eleve_dict.keys())
 #   for i in range(55,60):
 #       del eleve_dict[uptodate_eid[i]]
#

    uptodate_eid =set(eleve_dict.keys())
    int_database_eid = Eleves.objects.filter(ecole_id=sid).values_list('eid',flat=True)
    database_eid = set( str(eid) for eid in int_database_eid)

    eid_eleves_sorties= database_eid-uptodate_eid
    
    eleves_sorties = Eleves.objects.filter(eid__in =eid_eleves_sorties,ecole_id=sid)
    for eleve_sortie in eleves_sorties:
        print('5tal leves sortie '+eleve_sortie.nom+' '+str(eleve_sortie.uid))
        ElevesTransfer(
            uid=eleve_sortie.uid,
            nom=eleve_sortie.nom,
            prenom=eleve_sortie.prenom,
            date_naissance=eleve_sortie.date_naissance,
            arriv_sorti=False,
            sexe=eleve_sortie.sexe,
            level=eleve_sortie.classe.level,
            is_graduated=eleve_sortie.is_graduated,
            ecole_id=sid
        ).save()
    
    eleves_sorties.delete()

    #2 addin eleves_entree
    eid_eleves_arrives = uptodate_eid-database_eid   # on hold


    classes_ids = Classes.objects.filter(
        ecole_id=sid).values_list('cid', 'id')
    classes_ids_dic:dict = {}
    for cid, id in classes_ids:
        classes_ids_dic[str(cid)] = str(id)
    for eid_eleve_arrive in eid_eleves_arrives:
        eleve = eleve_dict[eid_eleve_arrive]
        classe_cid =eleve[5]
        Eleves(
            eid=eid_eleve_arrive,
            uid=eleve[0],
            nom=eleve[1],
            prenom=eleve[2],
            sexe=eleve[3],
            date_naissance=eleve[4],
            classe_id= classes_ids_dic[classe_cid],
            ecole_id=sid
        ).save()
        eleve_level = classes_dict[eleve[5]][1]
        ElevesTransfer(
            uid=eleve[0],
            nom=eleve[1],
            prenom=eleve[2],
            date_naissance=eleve[4],
            arriv_sorti=True,
            sexe=eleve[3],
            level=eleve_level,
            is_graduated=None,
            ecole_id=sid
        ).save()
        print('eleve ajoute f  zouz : ' +eleve_dict[eid_eleve_arrive][1])

    
    #3 update eleves
    uptodated_eid=uptodate_eid-eid_eleves_arrives   # on hold
    print(len(uptodated_eid))


    def bulk_update_eleves(eleve_dict):
        batch_size = 100  # Adjust this based on your database and performance testing
        array_eleves= list(eleve_dict.items())
        # Generate SQL updates and parameters for each batch
        for batch_start in range(0, len(array_eleves), batch_size):
            batch_end = batch_start + batch_size
            batch_updates = array_eleves[batch_start:batch_end]
            # Construct the SQL update statement
            sql = """
                UPDATE login_handler_eleves
                SET nom = CASE 
            """
            params = []
            for eid, (uid, nom, prenom, sexe, date_naissance, classe_id) in batch_updates:
                sql += f"WHEN eid = %s THEN %s "
                params.extend([eid, nom])

            sql += "END, uid = CASE "
            for eid, (uid, _, _, _, _, _) in batch_updates:
                sql += f"WHEN eid = %s THEN %s "
                params.extend([eid, uid])

            sql += "END, nom = CASE "
            for eid, (_, nom, _, _, _, _) in batch_updates:
                sql += f"WHEN eid = %s THEN %s "
                params.extend([eid, nom])

            sql += "END, prenom = CASE "
            for eid, (_, _, prenom, _, _, _) in batch_updates:
                sql += f"WHEN eid = %s THEN %s "
                params.extend([eid, prenom])
            
            sql += "END, sexe = CASE "
            for eid, (_, _, _, sexe, _, _) in batch_updates:
                sql += f"WHEN eid = %s THEN %s "
                params.extend([eid, sexe])

            sql += "END, date_naissance = CASE "
            for eid, (_, _, _, _, date_naissance, _) in batch_updates:
                sql += f"WHEN eid = %s THEN %s "
                params.extend([eid, date_naissance])

            sql += "END, classe_id = CASE "
            for eid, (_, _, _, _, _, classe_cid) in batch_updates:
                classe_id = classes_ids_dic[classe_cid]
                sql += f"WHEN eid = %s THEN %s "
                params.extend([eid, classe_id])

            sql += "END WHERE ecole_id= %s "
            params.append(sid)

            sql += "AND eid IN (%s)" % ','.join(
                ['%s'] * len(batch_updates))
            params.extend(eid for eid,(_) in batch_updates)

            # Execute the raw SQL update
            with connection.cursor() as cursor:
                cursor.execute(sql, params)


    bulk_update_eleves(eleve_dict)

    classes_to_delete =Classes.objects.filter(cid__in =deleted_classes,ecole_id=sid) 
    for cl in classes_to_delete:
        print('classes suprime :'+cl.name)
    classes_to_delete.delete()



def initiate2(dic):
    # zid l profet
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

    compare(classes_dict, eleve_dict, dic['sid'])
