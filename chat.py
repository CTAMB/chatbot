from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from json import JSONDecodeError
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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
    def __init__(self, conversation):
        self.conversation = conversation

    def lire_question(self):
        return input('Saisissez votre question .. ')



    def appel_openai(self):
        responses = client.responses.create(
        model = 'gpt-4.1-mini',
        input = self.conversation.conversation
        )
        return responses.output_text

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
        print(f"""Statistiques :
        Message utilisateur : {user}
        Message assistant : {assis}
        Total : {len(self.conversation.conversation)}
        """
        )
    def model(self):
        print('gpt-4.1-mini')




    



conversation = Conversation()
conversation.charger()


chatbot = Chatbot(conversation)
commande = Commande(conversation)




commandes = {
        "/help" : commande.aide,
        "/histo" : commande.historique,
        "/reset" : commande.reset,
        "/stats" : commande.stats,
        "/model" : commande.model
}

def verif_commandes(question):
    if question in commandes:
        commandes[question]()
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