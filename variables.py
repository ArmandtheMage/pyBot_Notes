import os
import json

#################################################
##### Import della costanti per la gestione #####
#####         e mantainance dei dati        #####
#################################################

with open("conf.json", "r+") as file:
    data = json.load(file)

MY_TOKEN = data["TOKEN"]


MY_ROLE = data["ROLEs_NAME"]                ### -> ["Master_Noter", "Bot_Noter", "Noter"]
MY_TERMINAL_FILE = data["TERMINAL_FILE"]    ### -> ["user", "common",  "secret"]
MY_CHANNEL_NAME = data["CHANNEL_NAME"]      ### -> ["user-notes", "common-notes",  "masters-secret"]
MY_SCOPE = data["SCOPE"]                    ### -> ["personal", "public", "master"]
MY_CLOCK_SIZE = [4, 6, 8]
BASE_PATH = os.path.join("asset", "images", "Clock")