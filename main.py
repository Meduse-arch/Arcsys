import discord
from discord.ext import commands
import random

#token bot
TOKEN = ''


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot connecté en tant que {bot.user}')
    await bot.tree.sync()

@bot.tree.command(name='hello', description='Salue l’utilisateur')
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f'Salut, {interaction.user.name} !')

@bot.tree.command(name='info', description='Donne des informations sur le bot')
async def info(interaction: discord.Interaction):
    await interaction.response.send_message('Je suis un bot Discord créé avec discord.py !')

# Commande clear
@bot.tree.command(name='clear', description='Supprime un certain nombre de messages.')
@discord.app_commands.checks.has_permissions(administrator=True)
async def clear(interaction: discord.Interaction, amount: int):
    if amount <= 0:
        await interaction.response.send_message('Vous devez spécifier un nombre positif de messages à supprimer.', ephemeral=True)
        return

    channel = interaction.channel
    deleted = await channel.purge(limit=amount)
    await interaction.response.send_message(f'J\'ai supprimé {len(deleted)} messages.', ephemeral=True)


@clear.error
async def clear_error(interaction: discord.Interaction, error):
    if isinstance(error, discord.app_commands.MissingPermissions):
        await interaction.response.send_message('Vous n\'avez pas la permission d\'utiliser cette commande.', ephemeral=True)

# Commande roll
@bot.tree.command(name='roll', description='Lance des dés avec un boost.')
async def roll(interaction: discord.Interaction, dice: int = 1, min: int = 1, max: int = 20, boost_pourcentage: int = 0, boost_nombre: int = 0):
    if dice <= 0:
        await interaction.response.send_message('Le nombre de dés doit être supérieur à 0.', ephemeral=True)
        return
    if min < 1:
        await interaction.response.send_message('La valeur minimale doit être au moins 1.', ephemeral=True)
        return
    if max < min:
        await interaction.response.send_message('La valeur maximale doit être supérieure à la valeur minimale.', ephemeral=True)
        return

    boosted_max = max + (max * (boost_pourcentage / 100))
    boosted_max_rounded = round(boosted_max)
    boost = boost_nombre + boosted_max_rounded

    results = [random.randint(min, boost) for _ in range(dice)]
    total = sum(results)

    if total < 0:
        total = 1
        print("je t'es sauvé") 


    response_message = f'🎲 {dice}d{min} à {boost} [{max} boost de {boost_pourcentage}% et {boost_nombre}] : {", ".join(map(str, results))}\n**Résultat**: {total}'

    if len(response_message) > 2000:
        await send_long_message(interaction.channel, response_message)
    else:
        await interaction.response.send_message(response_message)

# Commande apprentissage
@bot.tree.command(name='apprentissage', description='Effectue un apprentissage basé sur une stat.')
async def apprentissage(
    interaction: discord.Interaction, 
    stat: int, 
    difficulte: int, 
    boost_pourcentage: int = 0, 
    boost_nombre: int = 0, 
    erudit: str = 'G'
):

    if stat < 0:
        await interaction.response.send_message('La stat doit être positive.', ephemeral=True)
        return
    if difficulte < 1:
        await interaction.response.send_message('La difficulté doit être au moins 1.', ephemeral=True)
        return

    erudit_bonus = {'G' : 0, 'F': -1, 'E': -2, 'D': -3, 'C': -4, 'B': -5, 'A': -6, 'S': -7, 'N': -8, 'M': -9, 'T': -10, 'Z': -11}.get(erudit, 0)

    difficulte += erudit_bonus

    seuil_reussite = round(stat * 0.1 * difficulte)

    boosted_stat = stat + round(stat * (boost_pourcentage / 100)) + boost_nombre

    roll_result = random.randint(1, boosted_stat)

    reussite = roll_result >= seuil_reussite

    result_message = f'🎓 Apprentissage sur {boosted_stat} avec une difficulté de {difficulte} [boost de {boost_pourcentage}% et {boost_nombre}].\n'
    result_message += f'Lancement du dé: {roll_result}\n'
    result_message += f'Seuil de réussite: {seuil_reussite}\n'
    result_message += 'Résultat: ' + ('Réussite ! 🎉' if reussite else 'Échec. ❌')

    await interaction.response.send_message(result_message)


# split les messages
async def send_long_message(channel, message):
    for part in [message[i:i + 2000] for i in range(0, len(message), 2000)]:
        await channel.send(part)

bot.run(TOKEN)
