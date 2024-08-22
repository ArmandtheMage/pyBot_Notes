import os
import discord
from typing import List
from variables import *

################################
##### Funzioni di supporto #####
################################
    
#Cerca il canale in cui inserire la nota
async def get_my_channel(interaction:discord.Interaction, selectet_category:str, scope:int):
    if scope == 0:
        channel_name = f"{interaction.user.name.lower()}-notes"
    elif scope > 0: #includere anche la limitazione ???
        channel_name = f"{MY_CHANNEL_NAME[scope]}"
    else:
        print("Scope non gestito correttamente nella creazione/fetch del canale")

    fetched_category = discord.utils.get(interaction.guild.categories, name=selectet_category.capitalize())

    channel = discord.utils.get(interaction.guild.channels, name=channel_name, category=fetched_category)

    if fetched_category == None:
        fetched_category = await interaction.guild.create_category(name=selectet_category.capitalize())
        update_data(interaction=interaction, text=fetched_category.name, topic_or_category=1)
    
    if channel == None:
        #cambiare solo i privilegi di Noter
        #da testare o fare edit
        channel_overwrites = {discord.utils.get(interaction.guild.roles, name=MY_ROLE[0]): discord.PermissionOverwrite(view_channel=True, send_messages=False),
                              discord.utils.get(interaction.guild.roles, name=MY_ROLE[1]): discord.PermissionOverwrite(view_channel=True, send_messages=True),
                              interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False)}
        if scope == 2:
            channel_overwrites[discord.utils.get(interaction.guild.roles, name=MY_ROLE[2])] = discord.PermissionOverwrite(view_channel=False)
        else:
            channel_overwrites[discord.utils.get(interaction.guild.roles, name=MY_ROLE[2])] = discord.PermissionOverwrite(view_channel=True, send_messages=False)

        channel = await interaction.guild.create_text_channel(name=channel_name, category=fetched_category, overwrites=channel_overwrites)
    return channel


def get_data(interaction:discord.Interaction, topic_or_category:int, isClock:bool=False) -> List[str]:
    
    if topic_or_category == 0: #0 ---> TOPICs related to the user
        if isClock:
            file_paths = [os.path.join("data", f"{interaction.guild_id}", f"clock.txt")]
        else:
            file_paths = [os.path.join("data", f"{interaction.guild_id}", f"{interaction.user.name}.txt"),
                        os.path.join("data", f"{interaction.guild_id}", f"{MY_TERMINAL_FILE[1]}.txt")]
            if interaction.user == interaction.guild.owner:
                file_paths.append(os.path.join("data", f"{interaction.guild_id}", f"{MY_TERMINAL_FILE[2]}.txt"))
    elif topic_or_category == 1: #1 ---> CATEGORYs in the server
        file_paths = [os.path.join("data", f"{interaction.guild_id}", f"{interaction.guild_id}.txt")]
    else:
        print("Qualcosa è andato storto, selettore sbagliato!\nNon è possibile estrarre i topic o le categorie\n----Uscita in corso-----")
        return []

    data = []
    for file_path in file_paths:
        try:
            with open(file_path, "r") as file:
                read_content = file.readlines()
                for element in read_content:
                    if element not in data:
                        data.extend([element])
        except FileNotFoundError as e:
            print(f"Nessun file idoneo trovato, cercavo -> {file_path}")
    
    return data


def update_data(interaction:discord.Interaction, text:str, topic_or_category:int = 0, scope:int=None):
    if topic_or_category == 0 : #0 ---> TOPICs of the user
        if scope == 0:
            file_path = os.path.join("data", f"{interaction.guild_id}", f"{interaction.user.name}.txt")
        elif scope > 0 and scope < 3:
            file_path = os.path.join("data", f"{interaction.guild_id}", f"{MY_TERMINAL_FILE[scope]}.txt")
        elif scope == 3:
            file_path = os.path.join("data", f"{interaction.guild_id}", "clock.txt")
        else:
            print("Qualcosa è andato male, scope non gestito correttamente")
            return
        
    elif topic_or_category == 1 : #1 ---> CATEGORY
        file_path = os.path.join("data", f"{interaction.guild_id}", f"{interaction.guild_id}.txt")
    else:
        print("Qualcosa è andato storto, selettore sbagliato. Ne Topic ne Categoria . . .\nUscire!")
        return

    try:
        os.makedirs(os.path.split(file_path)[0])
    except FileExistsError as error:
        pass

    try:
        with open(file_path) as file:
            read_content = file.read()
            if text.capitalize() in read_content:
                print("Già presente non aggiornare il file")
            else:
                print("Topic o Categoria non presente!")
                file = open(file_path, "a+")s
                file.write(f"{text.capitalize()}\n")
    except FileNotFoundError as error:
        with open(file_path, "w+") as file:
            file.write(f"{text.capitalize()}\n")


async def handle_topic_delete(interaction:discord.Interaction, topic:str, scope:int):
    
    channels = interaction.guild.text_channels
    if scope == 0:
        channel_to_check = f"{interaction.user.name.lower()}-notes"
        terminal_file = f"{interaction.user.name.lower()}"
    elif scope > 0:
        channel_to_check = MY_CHANNEL_NAME[scope]
        terminal_file = MY_TERMINAL_FILE[scope]
    else:
        print("Scope Errato in **handel_topic_delete** . . . Uscita in corso")
        return

    for channel in channels:
        if channel.name == channel_to_check:
            async for message in channel.history():
                embeds = message.embeds
                if len(embeds) > 0:
                    embed = embeds[0]
                    if embed.title.capitalize() == topic.capitalize():
                        print("ancora altre note con questo topic")
                        return

    #Può essere inclusa in una funzione
    file_path = os.path.join("data", f"{interaction.guild_id}", f"{terminal_file}.txt")
    with open(file_path, "r") as file:
        read_content = file.readlines()

    try:
        read_content.remove(f"{topic.capitalize()}\n")
        print("Topic eliminato con successo")
    except ValueError as e:
        print("Per qualche motivo il topic è assente dal file")

    with open(file_path, "w+") as file:
        file.writelines(read_content)


def create_data(interaction:discord.Interaction, topics:str, scope:int, user:str=None):
    if scope == 0:
        terminal_file = f"{user}"
    elif scope >= len(MY_SCOPE):
        print("Scope Out of range in **create_data**\nUscire, qualcosa è andato storto . . .")
        return
    elif scope > 0:
        terminal_file = MY_TERMINAL_FILE[scope]
    else:
        terminal_file = f"{interaction.guild_id}"

    file_path = os.path.join("data", f"{interaction.guild_id}", f"{terminal_file}.txt")

    list_of_topic = topics.split("\n")

    try:
        os.makedirs(os.path.split(file_path)[0])
    except FileExistsError as error:
        pass

    try:
        with open(file_path, "a+") as file:
            file.write(f"{topics}")
    except FileNotFoundError as e:
        with open(file_path, "w+") as file:
            print("sono qui")
            file.write(f"{topics}")


async def handel_clock(interaction:discord.Interaction, text:str):
    channel = discord.utils.get(interaction.guild.text_channels, name="clocks")
    isToDel = True
    async for message in channel.history():
        if text in message.content:
            isToDel = False
            break
    
    if isToDel:
        file_path = os.path.join("data", f"{interaction.guild_id}", "clock.txt")
        with open(file_path, "r") as file:
            read_content = file.readlines()

        try:
            read_content.remove(f"{text.capitalize()}\n")
            print("Topic eliminato con successo")
        except ValueError as e:
            print("Per qualche motivo il topic è assente dal file")

        with open(file_path, "w+") as file:
            file.writelines(read_content)
