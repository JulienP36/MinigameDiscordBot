import os, sys
import random
import time
import traceback
import discord

#Différentes variables globales nécessaires pour le bon fonctionnement du bot
game_selected = "none"
intro = 0
compteur = 0
message_bot = 0
msg_lock = 0
client = discord.Client()
Grille = [[0] * 8 for z in range(8)]

#Fonction asynchrone permettant uniquement d'afficher dans la console l'id du bot dès que celui-ci est prêt
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

#Fonction asynchrone permettant de faire le lien entre l'utilisateur et le bot lorsque l'utilisateur envoi un message
@client.event
async def on_message(message):
    global game_selected
    global intro
    global compteur
    global message_bot
    global msg_lock
    # don't respond to ourselves
    if message.author == client.user:
        if msg_lock == 0:
            message_bot = message.id
            msg_lock = 1
        return
    if game_selected == "none":
        await menu(message)
    elif game_selected == "puissance4":
        if message.content.startswith("minigame!choix"):
            await puissance4(message)
        elif message.content.startswith("minigame!reset"):
            game_selected = "none"
            intro = 0
            compteur = 0
            msg_lock = 0
            await message.channel.send("Game reset !")

#Fonction asynchrone servant de menu pour lancer les différents jeux
@client.event
async def menu(message):
    global game_selected
    if message.content.startswith("minigame!help"):
        await message.channel.send("```Les commandes de ce bot commencent par 'minigames!' et sont suivies d'un suffixe.\n\nCommandes actuelles :\n - help\n - naval\n - puissance4\n\t - choix [1-8]\n\t - reset```")

    if message.content.startswith("minigame!naval"):
        await message.channel.send("Pas encore développé :frowning: voici un cookie pour patienter :cookie:")
        #game_selected = "naval"

    if message.content.startswith("minigame!puissance4"):
        game_selected = "puissance4"
        await puissance4(message)

#Fonction qui va effectuer le balayage de la grille de puissance 4 pour vérifier si l'un des joueurs est victorieux
def puissance4_winnerCheck():
    global Grille
    if (compteur - 1) % 2 == 0:
        num = 4
    else:
        num = 3
    for x in range(5):
        for y in range(8):
            if Grille[x][y] == Grille[x+1][y] == Grille[x+2][y] == Grille[x+3][y] in (1, 2):
                Grille[x][y], Grille[x+1][y], Grille[x+2][y], Grille[x+3][y] = num, num, num, num
                return "yes"
    for x in range(8):
        for y in range(5):
            if Grille[x][y] == Grille[x][y+1] == Grille[x][y+2] == Grille[x][y+3] in (1, 2):
                Grille[x][y], Grille[x][y+1], Grille[x][y+2], Grille[x][y+3] = num, num, num, num
                return "yes"
    for x in range(5):
        for y in range(5):
            if Grille[x][y] == Grille[x+1][y+1] == Grille[x+2][y+2] == Grille[x+3][y+3] in (1, 2):
                Grille[x][y], Grille[x+1][y+1], Grille[x+2][y+2], Grille[x+3][y+3] = num, num, num, num
                return "yes"
    for x in range(5):
        for y in range(5):
            if Grille[x][y] == Grille[x+1][y-1] == Grille[x+2][y-2] == Grille[x+3][y-3] in (1, 2):
                Grille[x][y], Grille[x+1][y-1], Grille[x+2][y-2], Grille[x+3][y-3] = num, num, num, num
                return "yes"
    return "no"

#Fonction qui va se lancer afin de permettre aux utilisateur de jouer à puissance4
#Todo: Donner la possibilité de changer la couleur des joueurs
@client.event
async def puissance4(message):
    global intro
    global Grille
    global compteur
    global game_selected
    global msg_lock
    gagnant = "no"
    msg_id = message.id
    if (compteur + 1) % 2 == 0:
        message_grille = "Au tour du Joueur jaune :"
    else:
        message_grille = "Au tour du Joueur rouge :"
    if intro == 0:
        compteur = 0
        intro = 1
        for i in range(8):
            message_grille = message_grille + "\n|"
            for j in range(8):
                Grille[i][j] = 0
                message_grille = message_grille + ":black_circle:|"
        await message.channel.send(message_grille + "\nPlacez un pion pour commencer : (numéro de colonne)")
    else:
        try:
            column = int(message.content.split()[1])
            if column >= 1 and column <= 8:
                if Grille[0][column-1] == 0:
                    for x in range(8):
                        if Grille[x][column-1] != 0:
                            Grille[x-1][column-1] = (compteur % 2) + 1
                            break
                        elif x >= 7:
                            Grille[x][column-1] = (compteur % 2) + 1
                            break
                    gagnant = puissance4_winnerCheck()
                    for i in range(8): #Composition du message à envoyer sous forme d'un seul et même message
                        message_grille = message_grille + "\n|"
                        for j in range(8):
                            if Grille[i][j] == 0:
                                message_grille = message_grille + ":black_circle:|"
                            elif Grille[i][j] == 1:
                                message_grille = message_grille + ":yellow_circle:|"
                            elif Grille[i][j] == 2:
                                message_grille = message_grille + ":red_circle:|"
                            elif Grille[i][j] == 3:
                                message_grille = message_grille + ":yellow_square:|"
                            elif Grille[i][j] == 4:
                                message_grille = message_grille + ":red_square:|"
                    compteur += 1
                    msg_bot = await message.channel.fetch_message(message_bot)
                    if compteur >= 64:
                        game_selected = "none"
                        intro = 0
                        msg_lock = 0
                        await message.channel.send("La partie est terminée ! Toute la grille a été remplie !")
                        if gagnant == "no":
                            await message.channel.send("Egalité !")
                    elif gagnant == "no":
                        #await message.channel.send(message_grille + "\nPlacez le prochain pion :")
                        await msg_bot.edit(content=message_grille + "\nPlacez le prochain pion :")
                    if gagnant == "yes":
                        game_selected = "none"
                        intro = 0
                        msg_lock = 0
                        if (compteur - 1) % 2 == 0:
                            await message.channel.send("Le joueur jaune a gagné !")
                        else:
                            await message.channel.send("Le joueur rouge a gagné !")
                        #await message.channel.send(message_grille)
                        await msg_bot.edit(content=message_grille)
                else:
                    msg_error = await message.channel.send("La colonne nunéro " + str(column) + " est déjà remplie !")
                    await msg_error.delete(delay=5)
            else:
                msg_error = await message.channel.send("L'argument donné n'est pas un chiffre valide\nrappel du format : `choix [1-8]`")
                await msg_error.delete(delay=5)

        except Exception as e:
            msg_error = await message.channel.send("Aucun argument donné, ou celui-ci est incorrect\nrappel du format : `choix [1-8]`")
            await msg_error.delete(delay=5)
            print(e)
            #traceback.print_exc() #utile mais seulement pour debug, à supprimer une fois le code validé
        msg_joueur = await message.channel.fetch_message(msg_id)
        await msg_joueur.delete(delay=1)


client.run('bot_token')

