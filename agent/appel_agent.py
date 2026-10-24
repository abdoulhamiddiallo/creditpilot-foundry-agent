"""Appel de l'agent CreditPilot depuis Python, avec le SDK Microsoft Foundry.

L'agent garde dans le portail ses instructions, son moteur de calcul, ses données
et sa politique : ce script lui envoie simplement deux questions dans la même
conversation, puis affiche ses réponses.

Prérequis, depuis la racine du dépôt :
    pip install -r agent/requirements.txt
    az login
Puis collez le point de terminaison de votre projet (page Accueil du projet Foundry)
dans POINT_DE_TERMINAISON, et lancez :
    python agent/appel_agent.py
"""
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

POINT_DE_TERMINAISON = "https://VOTRE-RESSOURCE.services.ai.azure.com/api/projects/proj-riskpilot"
NOM_AGENT = "creditpilot-ble"

projet = AIProjectClient(endpoint=POINT_DE_TERMINAISON, credential=DefaultAzureCredential())

# Client relié à l'agent : instructions, moteur de calcul, données et politique sont ceux du portail
client = projet.get_openai_client(agent_name=NOM_AGENT)
conversation = client.conversations.create()

print("Question 1 : note de risque complète (environ 30 secondes)\n")
reponse = client.responses.create(
    conversation=conversation.id,
    input="Rédige la note de risque de crédit complète pour le Comité des risques.",
)
print(reponse.output_text)

# Question de suivi dans la même conversation : l'agent garde le contexte
print("\n\nQuestion 2 : simulation\n")
suite = client.responses.create(
    conversation=conversation.id,
    input="Simule un scénario adverse pondéré à 100 % : que deviennent l'ECL, le ratio CET1 et le grand risque ?",
)
print(suite.output_text)
