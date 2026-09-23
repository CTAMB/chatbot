import os
import json
import csv
from dotenv import load_dotenv
from json import JSONDecodeError
from openai import OpenAI, APIConnectionError, RateLimitError
load_dotenv()


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


tools = [
    {
        "type" : "function",
        "name" : "stats",
        "description" : "Dès que je te parle du nombre de messages échangés dans la conversation. Je veux que tu sois juste, que ça soit mes messages où les tiens.",
        "parameters" : {"type" : "object",
                        "properties" : {},
                        "required" : [],
                        "additionalProperties": False
        }
    },
    {
        "type" : "function",
        "name" : "rechercher",
        "description" : "Recherche dans l'historique les messages contenant un mot. A utiliser quand l'utilisateur demande s'il a déjà parlé d'un sujet.",
        "parameters": {
            "type": "object",
            "properties": {
                "mot": {
                    "type": "string",
                    "description": "Le mot à rechercher dans l'historique"
                }
            },
            "required": ["mot"],
            "additionalProperties": False
        }
    },
    {
        "type" : "function",
        "name" : "depenses",
        "description" : "Recherche dans le fichier le nombre de dépenses pour la même catégorie et affiche le total du montant",
        "parameters": {
            "type" : "object",
            "properties" : {
                "categorie": {
                    "type": "string",
                    "description" : "la categorie à rechercher dans le fichier csv"
                }
            },
            "required" : ['categorie'],
            "additionalProperties" : False
        }

     }
]

class Conversation:
    def __init__(self):
        self.conversation = []

    def sauvegarder(self):
        with open('conversation.json', 'w') as f:
            json.dump(self.conversation, f)

    def charger(self):
        try:
            with open('conversation.json', 'r') as f:
                self.conversation = json.load(f)
        except FileNotFoundError:
            self.conversation = []
        except JSONDecodeError:
            self.conversation = []


    def ajouter_message(self, role, contenu):
        self.conversation.append({'role' : role, 'content' : contenu})
    
class Chatbot:
    def __init__(self, conversation, commande):
        self.conversation = conversation
        self.commande = commande

    def lire_question(self):
        return input('Saisissez votre question .. ')



    def appel_openai(self):
        try:
            responses = client.responses.create(
            model = 'gpt-4.1-mini',
            input = self.conversation.conversation,
            tools=tools
            )
            for element in responses.output:
                if element.type == 'function_call' and element.name == 'stats':
                    print('[outil stats appelé]')
                    resultat = self.commande.stats()
                    entree = self.conversation.conversation + [
                        element,
                        {"type": "function_call_output", "call_id": element.call_id, "output": resultat}
                    ]
                    responses = client.responses.create(
                        model='gpt-4.1-mini',
                        input=entree,
                        tools=tools
                    )
                    return responses.output_text


                elif element.type == 'function_call' and element.name == 'rechercher':
                    print('[outil rechercher appelé]')
                    arguments = json.loads(element.arguments)
                    mot = arguments['mot']
                    resultat = self.commande.rechercher(mot)
                    entree = self.conversation.conversation + [
                        element,
                        {"type": "function_call_output", "call_id": element.call_id, "output": str(resultat)}
                    ]
                    responses = client.responses.create(
                        model='gpt-4.1-mini',
                        input=entree,
                        tools=tools
                    )
                    return responses.output_text

                elif element.type == 'function_call' and element.name == "depenses":
                    print('[outil dépenses appelé]')
                    arguments = json.loads(element.arguments)
                    categorie = arguments['categorie']
                    resultat = self.commande.depenses(categorie)
                    entree = self.conversation.conversation + [
                        element,
                        {"type": "function_call_output", "call_id": element.call_id, "output": resultat}
                    ]
                    responses = client.responses.create(
                        model = "gpt-4.1-mini",
                        input=entree,
                        tools=tools
                    )
                    return responses.output_text
            return responses.output_text
        except APIConnectionError:
            return "Problème de connexion."
        except RateLimitError:
            return "Trop de requêtes ou quota dépassé."

class Commande:
    def __init__(self, conversation):
        self.conversation = conversation

    def aide(self):
        print("Voici les commandes : ")
        print("""
        /help --> Afficher les commandes
        /histo --> Afficher l'historique de la conversation
        /reset --> Supprimer la conversation
        /stats --> Afficher le nombre de message
        /model --> Afficher la version du client
        """
        )
    def historique(self):
        if self.conversation.conversation == []:
            print('Historique vide.')
        else:
            for nom in self.conversation.conversation:
                print(f"{nom['role']} : {nom['content']}")

    def reset(self):
        self.conversation.conversation.clear()
        print('Historique supprimée.')
        self.conversation.sauvegarder()


    def stats(self):
        user = 0
        assis = 0
        for nom in self.conversation.conversation:
            if nom['role'] == 'user':
                user += 1
            if nom['role'] == 'assistant':
                assis += 1
        return (f"""Statistiques :
        Message utilisateur : {user}
        Message assistant : {assis}
        Total : {len(self.conversation.conversation)}
        """
        )
    def model(self):
        print('gpt-4.1-mini')

    def rechercher(self, mot):
        liste = []
        for discussion in self.conversation.conversation:
            if mot in discussion['content']:
                liste.append(discussion['content'])
        if liste:
            return liste
        return f"Aucun message avec {mot} dedans."
    def depenses(self, categorie):
        with open('depenses.csv', 'r') as f:
            lecteur = csv.DictReader(f)
            total = 0
            c = 0
            for ligne in lecteur:
                if ligne["categorie"] == categorie:
                    total += float(ligne['montant'])
                    c += 1
            if c == 0:
                return f"Aucune dépense trouvée pour la catégorie {categorie}."
            return f'Total pour {categorie} : {total}€ sur {c} dépenses.'
                    
            
        



    



conversation = Conversation()
conversation.charger()

commande = Commande(conversation)
chatbot = Chatbot(conversation, commande)





commandes = {
        "/help" : commande.aide,
        "/histo" : commande.historique,
        "/reset" : commande.reset,
        "/stats" : commande.stats,
        "/model" : commande.model
}

def verif_commandes(question):
    if question in commandes:
        resultat = commandes[question]()
        if resultat:
            print(resultat)

        return True






while True:

    question = chatbot.lire_question()
    if verif_commandes(question):
        continue

    if question == '/quit':
        print('Fin de session.')
        break
    else:
        conversation.ajouter_message('user', question)

    reponse = chatbot.appel_openai()
    print(reponse)
    conversation.ajouter_message('assistant', reponse)
    conversation.sauvegarder()