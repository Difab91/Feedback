import os
import random
import re
import json
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
import Levenshtein
from files import liste_constants, liste_services

load_dotenv()

ollama_base_url = os.getenv("OLLAMA_BASE_URL")
ollama_model = os.getenv("OLLAMA_MODEL")

model = OllamaLLM(model=ollama_model, base_url=ollama_base_url)

# contexte apporter à l'IA
system_template = """Tu es un expert en migration d'applications AngularJS vers Angular 17, ton objectif est de retourner du code Angular 17 qui utilise les fonctionnalités modernes d'Angular 17 tout en maintenant les bonnes pratiques Angular actuelles."""


# prompt service 

human_template_service = (
    "genere moi le code converti d'un service AngularJS en service Angular 17 converti\n"
    "{{code2convert}} \n"  
    "genere le code complet de A à Z et ne fais pas de raccourcis\n"
    "#etapes\n"
    "1. **Mise à jour de la syntaxe** : Réécrivez le code en utilisant la syntaxe moderne d'Angular (version 17) et les nouveaux modèles, en veillant à utiliser TypeScript.\n"
    "2. **Injection de dépendances** : Transformez les services pour utiliser le décorateur @Injectable avec l'attribut providedIn pour déclarer la portée du fournisseur.\n"
    "3. **Adoption de RxJS** : Remplacez toute opération asynchrone par des Observables RxJS.\n"
    "4. **Injecter HttpClient** : Injecter HttpClient dans le service.\n"
    "5. **Performance** : Appliquez les bonnes pratiques de performance.\n"
    "6. **Cohérence de la logique métier** : Assurez-vous que la logique métier reste inchangée.\n"
    "7. **Typage strict avec TypeScript** : Utilisez le typage strict avec TypeScript."
)

#prompt constants

human_template_constant = (
    "transforme le code AngularJS suivant, en un service Angular moderne en utilisant @Injectable. "
    "Voici le code original en AngularJS que tu dois convertir en un code qui est service angular :{{code2convert}} /n"
)


# fonction qui choisis aléatoirement le type de fichier traiter , et parmis ce type choisis un fichier aléatoire parmis les 18
def choose_file():
    type_fichier = random.choice(['service', 'constants'])
    
    if type_fichier == 'service' and liste_services:
        chemin_fichier = random.choice(liste_services)
    elif type_fichier == 'constants' and liste_constants:
        chemin_fichier = random.choice(liste_constants)
    else:
        return None, None

    with open(chemin_fichier, 'r', encoding='utf-8') as f:
        contenu_fichier = f.read()

    return contenu_fichier, type_fichier

#########################  fct de conversion (fait appel au llm (codestral))  ##########################


def conversion(code_to_convert, chain):
    try:
        result = chain.invoke({"code2convert": code_to_convert})
        code_extracted = re.search(r"```typescript\n([\s\S]*?)\n```", result)
        if code_extracted:
            print("voici la conversion proposée :")
            print(code_extracted.group(1))
            return code_extracted.group(1)
        else:
            print("Aucun code trouvé dans la réponse.")
            return None
    except Exception as error:
        print(f"Une erreur s'est produite : {error}")
        return None
    
########################### Fonctions features data #########################################

def count_caracteres(code_source: str) -> int:
    return len(code_source)

def count_lines_of_code(code):
    return len(code.splitlines())

def levenshtein_distance(code1, code2):
    return Levenshtein.distance(code1, code2)

############################################################################################################

# Charger les données existantes et initialiser l'ID

data = []
last_id = 0

if os.path.exists('data.json'):
    with open('data.json', 'r') as f:
        data = json.load(f)
    last_id = max(item["id"] for item in data) if data else 0

# Boucle genere dataset manuellement
while True:
    last_id += 1
    choose_code_0, type_fichier = choose_file()
    choose_code_1 = f"{choose_code_0}"

    if type_fichier == "service":
        human_template = human_template_service
    elif type_fichier == "constants":
        human_template = human_template_constant

    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("human", human_template.format(code2convert=choose_code_1))
    ])

    chain = chat_prompt | model

    print("###############################")
    print("Start nouvelle boucle")
    print("###############################")
    print(f"Fichier choisi de type: {type_fichier}")
    print(f"Contenu du fichier:\n{choose_code_0}")
    print("###############################")
    print("Conversion en cours...")
    print("###############################")


    code_angular_converted = conversion(choose_code_1, chain) # conversion proposé par le llm avec le prompt correspondant au fichier choisis
    if not code_angular_converted:
        print("Erreur dans la conversion, on passe à un autre fichier.")
        continue

    label = int(input("La conversion est-elle correcte ? (0 = non, 1 = oui, 2 = skip, 3= stop) : "))

    if label == 2:
        print("On passe à un autre fichier.")
        continue

    if label == 3:
        break

    # add toutes les infos recuperer sur cette conversion à l'id

    data.append({
        "id": last_id,
        "code_angularjs": choose_code_0,
        "code_angular": code_angular_converted,
        "label": label,
        "features": {
            "type_code": type_fichier,
            "lines_of_code_js": count_lines_of_code(choose_code_1),
            "lines_of_code_angular": count_lines_of_code(code_angular_converted),
            "levenshtein_distance": levenshtein_distance(choose_code_1, code_angular_converted),
            "nbr_caractere_js": count_caracteres(choose_code_1),
            "nbr_caractere_angular": count_caracteres(code_angular_converted)
        }
    })


# save data dans le json

with open('data.json', 'w') as f:
    json.dump(data, f, indent=4)