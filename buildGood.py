from files import bad_constants, bad_services, bad_components, bad_dataservice, bad_restangular, good_restangular, good_components, good_constants, good_dataservice, good_services
import json
import os
from files import count_caracteres, count_lines_of_code, levenshtein_distance




def lier(liste_good, liste_bad ,type):
    good=[]
    for e in liste_good:
        name_good = os.path.basename(e).strip()[:-2]
        print(name_good)
        for f in liste_bad:
            if os.path.basename(f).strip()[:-2] == name_good:
                good.append([e,f,type])
    return good

rest= lier(good_restangular, bad_restangular, "restangular")
comp= lier(good_components, bad_components, "component")
cons= lier(good_constants, bad_constants, "constants")
datas= lier(good_dataservice, bad_dataservice, "dataservice")
serv= lier(good_services, bad_services, "restangular")

# listes "liant" le angular correct avec son angular js original, et son type pour tout les bon fichier angular réecrit
all= rest+comp+cons+datas+serv



print(len(all))
print(all)


data = []
last_id = 0

if os.path.exists('data.json'):
    with open('data.json', 'r') as f:
        data = json.load(f)
    last_id = max(item["id"] for item in data) if data else 0


for conv in all:
    code_angularjs=conv[1]
    with open(code_angularjs, 'r', encoding='utf-8') as f:
        code_angularjs = f.read()
    code_angular=conv[0]
    with open(code_angular, 'r', encoding='utf-8') as f:
        code_angular = f.read()

    type_fichier=conv[2]

    lines_js = count_lines_of_code(code_angularjs)
    lines_angular = count_lines_of_code(code_angular)
    dist_levenshtein = levenshtein_distance(code_angularjs, code_angular)
    caracteres_js = count_caracteres(code_angularjs)
    caracteres_angular = count_caracteres(code_angular)
    

    data.append({
        "id": last_id + 1,
        "code_angularjs": code_angularjs,
        "code_angular": code_angular,
        "label": 1,
        "features": {
            "type_code": type_fichier,
            "lines_of_code_js": lines_js,
            "lines_of_code_angular": lines_angular,
            "levenshtein_distance": dist_levenshtein,
            "nbr_caractere_js": caracteres_js,
            "nbr_caractere_angular": caracteres_angular
        }
    })
    last_id += 1

    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)
