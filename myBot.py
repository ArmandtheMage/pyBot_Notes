import os
import shutil
import discord
from discord.ext import commands
from discord import app_commands
import Views.MasterButton as masterView
import Views.JournalButton as button
import Views.ClockButton as clock
import Modals.ClockRename as clock_modal
from generic import *
from variables import *

################################
##### Main e class del Bot #####
################################

# Discord variables
intents = discord.Intents.all()

class BotClient(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or("!"), intents=intents)

        self.my_cogs = []
        for filename in os.listdir("./Cogs"):
            if filename.endswith(".py"):
                self.my_cogs.append(f"{filename[:-3]}")
                

    async def setup_hook(self):
        self.add_view(button.JournalButton())
        self.add_view(masterView.MasterButton())
        self.add_view(clock.ClockButton())
        for extention in self.my_cogs:
            await self.load_extension("Cogs." + extention)
        

    async def on_ready(self):
        # sostitire le print con log
        print(f'We have logged in as {client.user}')
        sync_cmds = await client.tree.sync()
        print(f"loaded {len(sync_cmds)} commands")


    async def on_guild_join(self, guild:discord.Guild):
        """Quando viene invitato in un server il bot controlla/recupera/assegna i ruoli necessari"""

        print(f"io sono {self.user} con ID: {self.user.id}")

        coulors = [discord.Colour.brand_red(), discord.Colour.green(), discord.Color.dark_blue()]
        #Check/Creazione Ruoli
        my_roles = []
        for i, role_name in enumerate(MY_ROLE):
            role = discord.utils.get(guild.roles, name=role_name)
            if role == None:
                role = await guild.create_role(name=role_name, mentionable=True, colour=coulors[i])
            
            print(f"{role} è assegnabile: {role.is_assignable()} e ha posizione: {role.position} ed è menzionabile {role.mentionable}")
            my_roles.append(role)

        #Assegnazione Ruoli
        for member in guild.members:
            print(f"\nAnalizzo {member.name}\n")
            if member == self.user:
                try:
                    await member.add_roles(my_roles[1])
                except discord.errors.Forbidden as e:
                    await guild.text_channels[0].send(content=f"```Possibile problema rilevato:\nNecessaria attività da parte dell'owner del server ---> Assegnare a me (BOT) il ruolo:```" + f"{my_roles[1].mention} → {member.mention}")
            elif member == guild.owner:
                if my_roles[0] in member.roles:
                    print(f"Il Master come previsto è sempre 3 passi avanti")
                else:
                    try:
                        await member.add_roles(my_roles[0])
                        print(f"{my_roles[0].name} aggiunto a {member.name}")
                    except discord.errors.Forbidden as e:
                        await guild.text_channels[0].send(content=f"Possibile problema rilevato:\nNecessaria attività da parte dell'owner del server ---> Assegnare a se stesso il ruolo:```" + f"{my_roles[0].mention} → {member.mention}")

            #role è già equivalente a my_roles[-1]
            if role in member.roles:
                print(f"{member.name} ha già il ruolo {role.name}")
            elif not member.bot:
                try:
                    await member.add_roles(role)
                except discord.errors.Forbidden as e:
                    await guild.text_channels[0].send(content=f"```Possibile problema rilevato:\nNecessaria attività da parte dell'owner del server ---> Assegnare il ruolo:```" + f"{my_roles[-1].mention} → {member.mention}")
                print(f"{role.name} aggiunto a {member.name}")
        
        #TODO Setup se il bot era già stato invitato
            

    async def on_member_join(self, member:discord.Member): 
        """Quando un nuovo membro viene aggiunto al server gli viene aggiunto il ruolo di Noter"""
        
        roles = member.guild.roles
        for role in roles:
            if MY_ROLE[-1] == role.name:
                print(f"Ruolo trovato!\n{role}")
                role2add = role

        if role2add == None:
            print("Quancosa fuori posto il ruolo Noter non esiste!")
        else:
            if role2add in member.roles:
                print("Qualcosa di strano, il membro non dovrebbe avere alcun ruolo perchè appena invitato")
            else:
                try:
                    await member.add_roles(role2add)
                except discord.errors.Forbidden as e:
                    await member.guild.text_channels[0].send(content=f"```Possibile problema rilevato:\nNecessaria attività da parte dell'owner del server ---> Assegnare al nuovo membro il ruolo```" + f"{role2add.mention} → {member.mention}")


    async def on_guild_remove(self, guild: discord.Guild):
        print(f"Eliminare ogni riferimento al server: {guild.name}\n```----EXTERMINATE----EXTERMINATE----EXTERMINATE```")
        #pulizia interna dei file
        print(f"guild {guild.name} no longer esisting removing {guild.id} files")
        file_path = os.path.join("data",f"{guild.id}")
        shutil.rmtree(file_path, ignore_errors=True)


    async def on_raw_member_remove(self, member:discord.RawMemberRemoveEvent):
        #discriminare se viene eliminato un Bot/Human
        if member.user.bot:
            print("Un bot è stato espulso niente da eseguire")
        else:
            #controllare cosa succede se si elimina l'owner del server
            print(f"Member {member.user.name} removed --> all the files in {member.guild_id} related must be destroyed!!!")
            file_path = os.path.join("data",f"{member.guild_id}", f"{member.user.name}.txt")
            try:
                os.remove(file_path)
            except FileNotFoundError as e:
                print(f"Apparentemente {member.user.name} non ha mai scritto una nota")

            channels = member.user.guild.text_channels
            for channel in channels:
                if member.user.name in channel.name:
                    await channel.delete()
                    print(f"Canale: {channel.name} eliminato")
        

    async def on_guild_channel_delete(self, channel:discord.TextChannel):
        category = channel.category
        if category == None:
            return
        elif len(category.channels) > 0 :
            return
        else:
            await category.delete()

            file_path = os.path.join("data", f"{channel.guild.id}", f"{channel.guild.id}.txt")
            #mettere in una funzione ?
            with open(file_path, "r") as file:
                read_content = file.readlines()
                
            try:
                read_content.remove(f"{category.name.capitalize()}\n")
                print("Topic eliminato con successo")
            except ValueError as e:
                print("Per qualche motivo il topic è assente dal file")

            with open(file_path, "w+") as file:
                file.writelines(read_content)


client = BotClient()

#COMANDO di reset per ricaricare le estensioni dinamicamente
@client.tree.command(name="load", description="Reload the cog, run only if something is changed")
@app_commands.choices(cog = [app_commands.Choice(name=cog, value=cog) for cog in client.my_cogs])
async def load(interaction: discord.Interaction, cog:app_commands.Choice[str]):
    try:
        await client.reload_extension(name="Cogs."+cog.value)
        await interaction.response.send_message(content=f"The commands in **{cog.value}** are reloaded and ready!")
    except Exception as e:
        await interaction.response.send_message(f"Error loading the command:\n```{e}```")

@client.tree.context_menu(name="full_clock")
async def full_clock(interaction:discord.Interaction, message:discord.Message):
    """Make a Clock Full"""
    file_name = message.attachments[0].filename
    new_path = os.path.join(BASE_PATH, f"Clock_{file_name[-7]}_{file_name[-7]}.png")

    view = clock.ClockButton()
    view.children[0].disabled = True

    await message.edit(attachments=[discord.File(new_path)], view=view)
    await interaction.response.send_message(content="Clock filled Succesfully!", ephemeral=True, delete_after=5)

@client.tree.context_menu(name="empty_clock")
async def empty_clock(interaction:discord.Interaction, message:discord.Message):
    """Make a Clock empty"""
    file_name = message.attachments[0].filename
    new_path = os.path.join(BASE_PATH, f"Clock_{file_name[-7]}_{'0'}.png")

    view = clock.ClockButton()
    view.children[1].disabled = True

    await message.edit(attachments=[discord.File(new_path)], view=view)
    await interaction.response.send_message(content="Clock emptied Succesfully!", ephemeral=True, delete_after=5)


@client.tree.context_menu(name="change_title")
async def change_title(interaction:discord.Interaction, message:discord.Message):
    if message.channel.name == "clocks":
        pass
    else:
        await interaction.response.send_message(content='Usa questo comando solo nel canale **"clocks"**', delete_after=5)
        return
    old_title = message.content[10:-3]
    print(old_title)
    await interaction.response.send_modal(clock_modal.ClockRename(message=message, old=old_title))


client.run(MY_TOKEN)

# permission Number = 27482690938960 
#https://discord.com/api/oauth2/authorize?client_id=1175142379431395430&permissions=27345923599600&scope=bot (EVENT)
# https://discord.com/api/oauth2/authorize?client_id=1175142379431395430&permissions=9745147620464&scope=bot
# https://discord.com/api/oauth2/authorize?client_id=1175142379431395430&permissions=8&scope=bot #admin