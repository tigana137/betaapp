import time
import requests
from bs4 import BeautifulSoup as bs

from login_handler.models import Classes




def verify_cnte(data):
    request = requests.session()
    url = data['ecole_url']+"acces.php"
    payload = {"saisieprenom": data['saisieprenom'],
               "saisienom": data['saisienom'],
               "saisiepasswd": data['saisiepasswd'],
               "saisie_membre": "administrateur",
               }
    response = request.post(url=url, data=payload)
    request.close()
    if "جديــد المدرســــــة" in response.text:
        return True
    else:
        return False


def verify_stat(data):
    request = requests.session()
    url = "http://stat.education.tn/index.php"
    payload = {"login": data['login'],
               "mp": data['mp']}
    page = request.post(url=url, data=payload)
    request.close()
    if "        متابعة حركة التلاميذ" in page.text:
        return True
    else:
        return False


def add_class(ecole_url, data):
    request = requests.session()
    url = ecole_url+'creat_classe.php'
    payload = {
        "saisie_niveau": data["saisie_niveau"],
        "saisie_creat_classe": data["saisie_creat_classe"],
        "saisie_classe_long": data["saisie_classe_long"],
        "create": "تسجيل"
    }
    response = request.post(url=url, data=payload)
    soup = bs(response.content.decode(
        encoding='utf-8', errors='ignore'), 'html.parser')
    script_tag = soup.find('script', {"type": 'text/javaScript'}).text

    if 'تمّ إنشاء قسم جديد' in script_tag:
        class_level = {"0": "التحضيري",  "1": "الأولى", "2": "الثانية", "3": "الثالثة",
                       "4": "الرابعة", "5": "الخامسة", "6": "السادسة"}   # maybe not that practical
        url = ecole_url+"consult_classe.php"
        response = request.post(url)
        soup = bs(response.text, 'html.parser')
        select_element = soup.find('select', {'id': 'saisie_classe'})
        class_list = select_element.find( 'option', string=class_level[data["saisie_niveau"]]+" : "+data["saisie_creat_classe"])
        class_id = class_list['value'].strip()
        class_ =Classes(id=class_id)
        class_.name = data["saisie_creat_classe"]
        class_.level = data["saisie_niveau"]
        class_.count=0
        class_.male_count=0
        class_.female_count=0
        class_.save()
        request.close()
        return True
    elif 'يوجد قسم بهذا الإسم':
        request.close()
        return False
    else:
        request.close()
        return False




def del__class(ecole_url,data):
    request = requests.session()
    url = ecole_url+"suppression_classe.php"
    payload={"saisie_classe_supp": data["saisie_classe_supp"], "supp": "حذف  قسم"}
    response = request.post(url=url, data=payload)
    soup = bs(response.text, 'html.parser')
    script_tag = soup.find('script', {"type": 'text/javaScript'}).text
    if "تمّ حذف القسم" in script_tag:
        request.close()
        return True
    elif " لحذف هذا القسم يجب حذف التلاميذ و حذف الإسناد. " in script_tag:
        request.close()
        return False
    else:
        request.close()
        return False
    


