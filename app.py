import streamlit as st
import os
import random
import re
import json
import time
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from files import count_caracteres, count_lines_of_code, levenshtein_distance
from files import bad_constants, bad_services, bad_components, bad_dataservice, bad_restangular

load_dotenv()

ollama_base_url = os.getenv("OLLAMA_BASE_URL")
ollama_model = os.getenv("OLLAMA_MODEL")
model = OllamaLLM(model=ollama_model, base_url=ollama_base_url)

# Contexte IA
system_template = """Tu es un expert en migration d'applications AngularJS vers Angular 17, ton objectif est de retourner du code Angular 17 qui utilise les fonctionnalités modernes d'Angular 17 tout en maintenant les bonnes pratiques Angular actuelles."""

# Prompts
human_template_service = (
    "converti moi ce service AngularJS en service angular 17:\n" 
  "{{code2convert}} \n" 
 """  Mise à jour de la syntaxe : Réécrivez le code en utilisant la syntaxe moderne d'Angular et les nouveaux modèles, en veillant à utiliser TypeScript. 
  Injection de dépendances: Transformez les services pour utiliser le décorateur @Injectable avec l'attribut providedIn pour déclarer la portée du fournisseur. 
 Cohérence de la logique métier : Assurez-vous que la logique métier reste inchangée pendant la transformation. 
  Typage strict avec TypeScript : Mettez en place un typage strict dans tout le code à l'aide du système de types de TypeScript. 
  genere bien le code en entier avec toutes les methodes """
)
 

human_template_daraservice = (
    "converti moi ce service AngularJS en service angular 17:\n" 
"{{code2convert}} \n" 
"""Mise à jour de la syntaxe : Réécrivez le code en utilisant la syntaxe moderne d'Angular et les nouveaux modèles, en veillant à utiliser TypeScript. 
Injection de dépendances: Transformez les services pour utiliser le décorateur @Injectable avec l'attribut providedIn pour déclarer la portée du fournisseur. 
Adoption de RxJS : Remplacez toute opération asynchrone par des Observables RxJS pour une programmation réactive en TypeScript. 
inject un httpClient : injecter HttpClient dans un service en le spécifiant dans la liste des dépendances du constructeur du service (import ' HttpClient, Observable' dans le code) 
Cohérence de la logique métier : Assurez-vous que la logique métier reste inchangée pendant la transformation. 
Typage strict avec TypeScript : Mettez en place un typage strict dans tout le code à l'aide du système de types de TypeScript. 
genere bien le code en entier avec toutes les methodes  et precise les const url dans les methodes 
 """ 

)

human_template_restangular = (
"genere moi le code converti d'un factory AngularJS en service angular moderne converti\n" 
  "ce code est un service qui fait appel directement au donnee de plus bas niveau:" 
  "{{code2convert}} \n" 
  "Fait le CRUD avec les methodes get, post, put, delete si nécessaire\n" 
  "Remplace toute opération asynchrone par des Observables RxJS/n" 
  "utiliser le décorateur @Injectable avec l'attribut providedIn pour déclarer la portée du fournisseur/n" 
  "si on fait appel à un restangular met le dans le constructor" 
)

human_template_components = (
   """Follow these guidelines to transform your AngularJS code 
# Prime directive: 
Transform the following AngularJS code using Angular 2+ standards. Make sure to: 
1. Use modern Angular 2+ syntax and patterns 
2. Use standalone components 
3. Use signals for state management where appropriate 
4. Use the inject() function in components to obtain service instances where appropriate
5. Apply performance best practices 
6. Keep the same business logic 

# Specific instructions : 

- Break down AngularJS controllers into components 
- Preserve variable/function names unless they do not conform to Angular conventions 
- Use TypeScript with strict typing 
- Implements the appropriate lifecycle hooks 
- Adapts dependency management for Angular 2+ 
- Angular 2+ services are located in @services/serviceName. 
- Angular 2+ services use Observable 

## AngularJS controller source code 
{{code2convert}} """


)



human_template_constant = (
   """Convertir ce fichier de constantes AngularJS en un fichier compatible avec Angular moderne : {{code2convert}}
   consignes détaillées pour la conversion : utilise un injectable et readonly 
   #Étapes : 1.**Syntaxe moderne et TypeScript** : Convertir le code en TypeScript en suivant la syntaxe d'Angular 16. 
   # Remplacer les anciennes définitions de constantes globales par des modules de constantes modernes en Angular. 
   # Toutes les constantes doivent être fortement typées. 
   # 2.**Typage strict avec TypeScript **: Met en place un typage strict pour toutes les constantes et les objets. 
   # Assure toi que chaque constante est typée correctement (par exemple string, number, boolean, ou des types complexes comme Observable ou des interfaces personnalisées). """
)

# Fonction pour sélectionner un fichier aléatoire
def choose_file():
    type_fichier = random.choice(['service', 'constants','dataservice','restangular','component'])
    
    if type_fichier == 'service' and bad_services:
        chemin_fichier = random.choice(bad_services)
    elif type_fichier == 'constants' and bad_constants:
        chemin_fichier = random.choice(bad_constants)
    elif type_fichier == 'component' and bad_components:
        chemin_fichier = random.choice(bad_components)
    elif type_fichier == 'dataservice' and bad_dataservice:
        chemin_fichier = random.choice(bad_dataservice)
    elif type_fichier == 'restangular' and bad_restangular:
        chemin_fichier = random.choice(bad_restangular)
    else:
        return None, None

    with open(chemin_fichier, 'r', encoding='utf-8') as f:
        contenu_fichier = f.read()

    return contenu_fichier, type_fichier, chemin_fichier

# Fonction de conversion utilisant le modèle
def conversion(code_to_convert, chain):
    try:
        result = chain.invoke({"code2convert": code_to_convert})
        code_extracted = re.search(r"```typescript\n([\s\S]*?)\n```", result)
        if code_extracted:
            return code_extracted.group(1)
        else:
            return None
    except Exception as error:
        st.error(f"Erreur dans la conversion : {error}")
        return None


# Chargement des données JSON existantes
data = []
last_id = 0

if os.path.exists('data.json'):
    with open('data.json', 'r') as f:
        data = json.load(f)
    last_id = max(item["id"] for item in data) if data else 0

st.title("Labelisation Automatique")

# Boucle principale de conversion
while True:
    # Choisir un fichier
    choose_code_0, type_fichier, chemin = choose_file()
    if not choose_code_0:
        st.warning("Aucun fichier disponible.")
        break
    
    choose_code_1 = f"{choose_code_0}"
    
    if type_fichier == "service":
        human_template = human_template_service
    elif type_fichier == "constants":
        human_template = human_template_constant
    elif type_fichier == "component":
        human_template = human_template_components
    elif type_fichier == "dataservice":
        human_template = human_template_daraservice
    elif type_fichier == "restangular":
        human_template = human_template_restangular

    # Création du prompt
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("human", human_template.format(code2convert=choose_code_1))
    ])
    chain = chat_prompt | model

    # Conversion du code
    code_angular_converted = conversion(choose_code_1, chain)

    if not code_angular_converted:
        st.warning("Erreur dans la conversion, passage au fichier suivant.")
        continue

    # Afficher les résultats
    st.subheader("Code AngularJS Original")
    st.code(choose_code_0, language='javascript')

    st.subheader("Code Converti en Angular")
    st.code(code_angular_converted, language='typescript')

    st.write("## Informations de la conversion")
    lines_js = count_lines_of_code(choose_code_1)
    lines_angular = count_lines_of_code(code_angular_converted)
    dist_levenshtein = levenshtein_distance(choose_code_1, code_angular_converted)
    caracteres_js = count_caracteres(choose_code_1)
    caracteres_angular = count_caracteres(code_angular_converted)

    st.write(f"**Nombre de lignes (AngularJS)** : {lines_js}")
    st.write(f"**Nombre de lignes (Angular 17)** : {lines_angular}")
    st.write(f"**Distance de Levenshtein** : {dist_levenshtein}")
    st.write(f"**Nombre de caractères (AngularJS)** : {caracteres_js}")
    st.write(f"**Nombre de caractères (Angular 17)** : {caracteres_angular}")
    st.write({chemin})

    # Attendre 5 secondes avant d'attribuer automatiquement le label "Incorrecte"
    st.write("Analyse en cours, label par défaut dans 5 secondes...")
    time.sleep(2)
    label = "Incorrecte"  # Label par défaut après 5 secondes
    st.warning("Label 'Incorrecte' attribué automatiquement.")

    # Sauvegarder les données
    data.append({
        "id": last_id + 1,
        "code_angularjs": choose_code_0,
        "code_angular": code_angular_converted,
        "label": 0,  # Incorrecte = 0
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

    st.info("Nouvelle conversion en cours...")
