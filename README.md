# Chatbot OpenAI

Chatbot utilisant l'API d'OpenAI, a comme possibilité de compter le nombre d'échanges dans la conversation et retrouver les messages qui contiennent un mot, à la demande de l'utilisateur.

## Fonctionnalités
- Messagerie instantanée avec IA
- Conversation sauvegardée en JSON
- Gestion d'erreurs réseau
- Tool Calling avec deux outils (stats et rechercher)

## Commandes
- /help : affiche toutes les commandes du chatbot
- /histo : Afficher l'historique de la conversation.
- /reset : Supprimer la conversation.
- /stats : Afficher le nombre de message.
- /model : Afficher la version du client.
- /quit : Sortir du programme.


## Comment fonctionne le tool calling
1. Le programme envoie au modèle l'historique de la conversation et la liste des outils disponibles (tools)
2. Le modèle décide s'il a besoin d'un outil et, au lieu de répondre en texte, il envoie une demande d'appel : element.
3. Le programme execute la méthode demandée et recupere le resultat.
4. Le programme fait un second appel, parce que le modèle ne conserve rien en mémoire. On lui renvoie l'historique, sa demande et le résultat, relié par le call_id.
5. Le modèle lit le résultat et rédige une réponse finale en langage naturel.