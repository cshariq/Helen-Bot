from collections import defaultdict
from discord.ext import commands
from PIL import Image, ImageDraw
import google.generativeai as genai
from discord import app_commands
from langdetect import detect
from googletrans import Translator
from time import sleep
import unicodedata
import keyboard
import requests
import discord
import asyncio
import random
import re
import os

intents = discord.Intents.all()
intents.messages = True
bot = commands.Bot(command_prefix="a", intents=intents, allowed_mentions = discord.AllowedMentions.none())
words_to_detect = ["i'm", "i’m", "im", "i am", "je suis", "am i", "are you", "ru", "r u", "suis je", "you're", "you are", "ur", "u r", "are u", "tu est", "est tu", "est-tu"]

allowed_characters = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ")
token = "Gemini-Token Key"
channel_id = 1208611858001690715
genai.configure(api_key="Gemini-API-Key")

class ChatSession:
    def __init__(self, length, platform, instruction, items = None):
        generation_config = {
        "temperature": length,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
        }
        safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_LOW_AND_ABOVE",
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_LOW_AND_ABOVE",
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_LOW_AND_ABOVE",
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_LOW_AND_ABOVE",
        },
        ]
        print(platform)
        self.model = genai.GenerativeModel(platform, generation_config=generation_config, safety_settings=safety_settings, system_instruction=instruction)
        self.chat = self.model.start_chat(history=[])

    def send_message(self, message):
        response = self.chat.send_message(message)
        response.resolve()
        # print(self.chat.history)
        return response

    def get_chat_history(self):
        return self.chat.history

class BotData:
    def __init__(self):
        self.bozo = 0
        self.nice = 0
        self.ur_mom = 0
        self.no_u = 0
        self.si = 0
        self.ie = 0
        self.rg = 0
        self.ry = 0
        self.sleeps = 0
        self.skips = 0
        self.moyais = 0
        self.im_callouts = 0
        self.correction_callouts = 0
        self.skip = False
        self.sleeping = False
        self.messagess = 0
        self.rate_limit = 0
        self.number = 0
        self.ai = 0
        self.previous_message = any
chat_sessions = defaultdict(ChatSession)
bot_data = BotData()

# Interaction weights
interaction_weights = {
    'direct_message': 4,
    'mention': 3,
    'reaction': 2,
    'same_channel': 1
}
interactions = defaultdict(int)
# Async function to process all messages in the bot's guilds
async def process_all_messages(bot):
    interactions = defaultdict(int)
    for guild in bot.guilds:
        for channel in guild.channels:
            if isinstance(channel, discord.TextChannel):
                async for message in channel.history(limit=5):
                    os.system('cls')
                    print("Channel: " + channel.name)
                    if not message.author.bot:
                        await process_message(bot, message, interactions)
    return interactions

# Async function to process individual messages
async def process_message(bot, message, interactions):
    if message.author == bot.user:
        return
    print("Author: " + message.author.name)
    for reaction in message.reactions:
        print("collecting reactions")
        async for user in reaction.users():
            if user != bot.user:
                print("Reaction: " + user.name)
                interactions[(message.author.name, user.name)] += interaction_weights['reaction']
    if isinstance(message.channel, discord.DMChannel):
        print("collecting dm's")
        other_user = message.channel.recipient
        print("Dm's: " + other_user)
        interactions[(message.author.name, other_user.name)] += interaction_weights['direct_message']
    mentions = message.mentions
    for user in mentions:
        print("collecting mentions")
        print("Mentions: " + user.name)
        if user != bot.user:
            interactions[(message.author.name, user.name)] += interaction_weights['mention']

@bot.event
async def on_reaction_add(reaction, user):
    message = reaction.message
    if user != bot.user and message.author != bot.user:
        interactions[(user.name, message.author.name)] += interaction_weights['reaction']

async def prompt_ai(message, id = None, image = None, platform = 'gemini-1.5-flash', length = 0, history = None, instruction = "Ton nom est helen, et tu parle en francais", interaction = True):
    current_message = message
    bot_data.ai += 1
    if interaction:
        if message.reference is not None:
            history = []
            while current_message.reference is not None:
                current_message = await current_message.channel.fetch_message(current_message.reference.message_id)
        if not current_message.id in chat_sessions:
            chat_sessions[current_message.id] = ChatSession(length, platform, instruction, history)
    else:
        chat_sessions[id] = ChatSession(length, platform, instruction, history)
    if not interaction:
        return (chat_sessions[id].send_message(message)).text
    elif not image == None:
        return (chat_sessions[current_message.id].send_message([message.clean_content, image])).text
    else:
        return (chat_sessions[current_message.id].send_message(message.clean_content)).text
# Function to calculate compatibility between two users
def calculate_compatibility(user1: discord.User, user2: discord.User, interactions):
    score = interactions[(user1.name, user2.name)] + interactions[(user2.name, user1.name)]
    print(score)
    return score

# Function to get the rate limit for the bot
def get_rate_limit(token, channel_id):
    response = requests.get(f"https://discord.com/api/v9/channels/{channel_id}", headers={"Authorization": f"Bot {token}"})
    if response.status_code == 200:
        data = response.json()
        rate_limit = data["rate_limit_per_user"]
        print(f"rate_limit")
    return rate_limit

@bot.tree.command(name="coin_flip", description = "the name legit says it, it flips a coin")
async def coin_flip(interaction):
    result = 'Heads' if random.randint(0, 1) == 0 else 'Tails'
    await interaction.response.send_message(f'Coin flip result: {result}', ephemeral=False)

@bot.tree.command(name="smart", description = "idk just ai guys but fast")
@app_commands.describe(question="Enter your question", length="The length of the response, higher the longer", platform = "The platform of your choice")
@app_commands.choices(platform=[
    app_commands.Choice(name="Fast", value="gemini-1.5-flash"),
    app_commands.Choice(name="Smart", value="gemini-1.5-pro")
])
async def smart(interaction: discord.Interaction, question: str, length: app_commands.Range[float, 0, 1] = 0, platform: str = 'gemini-1.5-flash', instruction: str = "Ton nom est helen, et tu parle en francais"):
    await interaction.response.send_message(await prompt_ai(question, interaction.id, None, platform, length, None, instruction, False))
    temp_session = chat_sessions[interaction.id]
    del chat_sessions[interaction.id]
    original_message = await interaction.original_message()
    print(original_message.id)
    chat_sessions[original_message.id] = temp_session
    
# Slash command to display bot data
@bot.tree.command(name='data', description = "dw abt it, just shows bot action history")
async def datas(interaction):
    await interaction.response.send_message(str(bot_data))

# Slash command to ship two users
@bot.tree.command(name='ship', description = "Matchmaker but with acc facts")
async def ship(interaction: discord.Interaction, user1: discord.User = None, user2: discord.User = None):
    if user1 is None: 
        user1 = interaction.user
    if user2 is None: 
        user2 = random.choice(interaction.guild.members)
        while user2 == user1 or user2.bot:
            user2 = random.choice(interaction.guild.members)
    compatibility = calculate_compatibility(user1, user2, interactions)
    name1 = user1.nick if user1.nick else user1.name
    name2 = user2.nick if user2.nick else user2.name
    ship_name = name1[:len(name1)//2] + name2[len(name2)//2:]
    message = "JNSP"
    if compatibility > 100:
        message = "Exceptional 😍😍😍"
        heart = Image.open('Heart_Struck.png').convert('RGBA')
    elif compatibility == 100:
        message = "Excellent 😍"
        heart = Image.open('Heart_100.png').convert('RGBA')
    elif compatibility >= 90:
        message = "Amazing 🤩"
        heart = Image.open('Heart2x.png').convert('RGBA')
    elif compatibility >= 80:
        message = "Pretty Good 😄"
        heart = Image.open('Heart2x.png').convert('RGBA')
    elif compatibility >= 70:
        message = "Good 🙂"
        heart = Image.open('Heart.png').convert('RGBA')
    elif compatibility >= 50:
        message = "Good Enough 😐"
        heart = Image.open('Heart.png').convert('RGBA')
    elif compatibility >= 40:
        message = "Fine 🥲"
        heart = Image.open('Broken_Heart.png').convert('RGBA')
    elif compatibility >= 30:
        message = "Nahhh 😢"
        heart = Image.open('Broken_Heart.png').convert('RGBA')
    elif compatibility <= 30:
        message = "Terrible 😭"
        heart = Image.open('Broken_Heart.png').convert('RGBA')
    filled_heart = '🟪'
    progress_bar = (filled_heart * round(compatibility / 10))
    def create_circle_mask(size):
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        return mask
    avatar1 = Image.open(requests.get(user1.avatar.url, stream=True).raw)
    avatar2 = Image.open(requests.get(user2.avatar.url, stream=True).raw)
    heart = heart.resize((150, 150), Image.LANCZOS)
    avatar1 = avatar1.resize((128, 128), Image.LANCZOS)
    avatar2 = avatar2.resize((128, 128), Image.LANCZOS)
    mask1 = create_circle_mask(avatar1.size)
    mask2 = create_circle_mask(avatar2.size)
    avatar1 = Image.composite(avatar1, Image.new('RGBA', avatar1.size), mask1)
    avatar2 = Image.composite(avatar2, Image.new('RGBA', avatar2.size), mask2)
    new_image = Image.new('RGBA', (avatar1.width + avatar2.width + heart.width + 20, avatar1.height))  # Add 20 pixels for space
    new_image.paste(avatar1, (0, 0))
    new_image.paste(avatar2, (avatar1.width + heart.width + 20, 0))
    heart_position = ((new_image.width - heart.width) // 2, 0)
    new_image.alpha_composite(heart, heart_position)
    new_image.save('new_image.png')
    embed = discord.Embed(title="Compatibility", color=0xFF69B4)
    embed.add_field(name="Compatibility", value=f"`{compatibility}%! {message}\n{progress_bar}`", inline=False)
    embed.set_image(url='attachment://new_image.png')
    await interaction.response.send_message(f"💗 MATCHMAKING 💗\n🔻 `{name1}`\n🔺 `{name2}`", file=discord.File('new_image.png', 'new_image.png'), embed=embed)

@bot.event
async def on_ready():
    print(bot_data.sleeping)
    await bot.tree.sync()
    mode = input("Are 2 people running this or 1: ").strip()
    channel = bot.get_channel(channel_id)
    if mode == "2":
        async for message in channel.history(limit=100):
            try:
                bot_data.number = int(message.content) + 1
                await asyncio.sleep(1)
                print("The current number is " + str(bot_data.number))
                print("Ready \n Go ahead and type the next number")
                bot_data.rate_limit = get_rate_limit(token, channel_id)
                print("You got " + str(bot_data.rate_limit))
                sleep(bot_data.rate_limit)
                break
            except:
                await asyncio.sleep(0.3)
                pass
    else:
        async for message in channel.history(limit=100):
            try:
                bot_data.number = int(message.content) + 1
                await asyncio.sleep(1)
                break
            except:
                await asyncio.sleep(0.3)
                pass
    os.system('clear')
    print("looking for user interactions...")
    if not interactions:
        os.system('clear')
        print("processing user interactions...")
        print("This will take a few minutes")
        await process_all_messages(bot)
    print(interactions)
    print("The current number is " + str(bot_data.number))
    print("Ready")
    bot_data.rate_limit = get_rate_limit(token, channel_id)

async def send_number(channel, number, rate_limit):
    keyboard.write(str(number + 2))
    number += 2
    keyboard.press_and_release("Enter")
    await asyncio.sleep(rate_limit)
    return number
    
@bot.event
async def on_message(message):
    bot_data.messagess += 1
    await process_message(bot, message, interactions)
    channel = bot.get_channel(message.channel.id)
    async def text(content):
        await channel.send(content, reference = message, allowed_mentions = None)
    try:
        detected_language = detect(str(message.content))
        if not detected_language == 'en' and not message.author == bot.user:
            translator = Translator()
            await text(translator.translate(str(message.content), dest='en').text)
    except Exception as e:
        print(f"Error: {e}")
    if message.attachments:
        attachment = message.attachments[0]
        if (
            attachment.filename.endswith(".jpg")
            or attachment.filename.endswith(".jpeg")
            or attachment.filename.endswith(".png")
            or attachment.filename.endswith(".webp")
            or attachment.filename.endswith(".gif")
        ):
            img_data = requests.get(attachment.url).content
            with open("/home/pi/image_name.jpg", "wb") as handler:
                handler.write(img_data)
            img = Image.open('/home/pi/image_name.jpg')
        await text(await prompt_ai(message, None, img))
    elif bot.user in message.mentions:
        bot_data.previous_message = message
        await text(await prompt_ai(message))
    else:
        bot_data.previous_message = message
            
    if message.channel.id == 1208610273506885676 or message.channel.id == 1208610273506885677 or message.channel.id == 1208907273175437382:
        if random.randint(1, 20) == 10:
            bot_data.skip = True
            bot_data.sleeps += 1
        else:
            bot_data.skip = False
        if random.randint(1, 150) == 75:
            bot_data.sleeping = True
            bot_data.sleeps += 1
            await text("Sleeping...")
            asyncio.sleep(300)
            bot_data.sleeping = False
    else:
        if random.randint(1, 100) == 50:
            bot_data.previous_message = message
            await text(await prompt_ai(message))
        bot_data.skip = False

    if not bot_data.skip and not bot_data.sleeping:
        if random.randint(1, 100) == 50:
            await text("L bozo")
            bot_data.bozo += 1 
        elif random.randint(1, 200) == 100:
            await text("nice")
            bot_data.nice += 1
        elif random.randint(1, 300) == 150:
            await text("ur mom")
            bot_data.ur_mom += 1
        elif random.randint(1, 150) == 500:
            await text("skill issue")
            bot_data.si += 1
        elif random.randint(1, 250) == 500:
            await text("no u")
            bot_data.no_u += 1
        elif random.randint(1, 700) == 350:
            await text("https://tenor.com/view/rick-roll-rick-ashley-never-gonna-give-you-up-gif-22113173")
            bot_data.rg += 1
        elif random.randint(1, 10000) == 1000:
            await text("<https://www.youtube.com/watch?v=GFq6wH5JR2A>")
            bot_data.ry += 1
        try:
            emoji = unicodedata.lookup(str(message.content).strip())
            await message.add_reaction(emoji)
        except:
            try:
                emoji = unicodedata.lookup(str(message.content).strip() + " face")
                await message.add_reaction(emoji)
            except:
                pass

        if not message.author == bot.user:
            original_message = message.content
            cropped_message = None
            pattern = re.compile(r'\b(?:' + '|'.join(re.escape(word) for word in words_to_detect) + r')\b', re.IGNORECASE)
            matches = pattern.findall(original_message.lower())
            if matches:
                for last_keyword in matches:
                    start_index = original_message.lower().rindex(last_keyword) + len(last_keyword)
                    cropped_message = original_message[start_index:].lstrip()
                    first_word = cropped_message.split()[0] if cropped_message else ""
            if cropped_message is not None:
                if last_keyword == "je suis":
                    await text(f"bonjour {cropped_message} \nje suis helen")
                    bot_data.im_callouts += 1
                elif last_keyword in ["are you", "ru", "r u", "you're", "you are", "ur", "u r", "are u"]:
                    if message.mentions:  # If the list is not empty
                            author = message.mentions[0].nick
                            if author == None:
                                author = message.mentions[0].name
                    else:
                        try:
                            messages = await channel.fetch_message(message.reference.message_id)
                            author = str(messages.author.display_name).lower()
                        except:
                            continue_loop = True
                            async for message_content in channel.history(limit=100):
                                successful_try = False
                                if str(message_content.author.display_name).lower() == str(message.author.display_name).lower():
                                    try:
                                        messages = await channel.fetch_message(message_content.reference.message_id)
                                        author = str(messages.author.display_name).lower()
                                        successful_try = True
                                    except:
                                        author = "someone"
                                else:
                                    author = str(message_content.author.display_name).lower()
                                    break
                                if successful_try:
                                    break
                    if re.sub(r'\W', ' ', author).lower().strip() == re.sub(r'\W', ' ', first_word).lower().strip():
                        await text("yes they're " + author)
                    else:
                        await text("no they're " + author)
                    bot_data.correction_callouts += 1
                elif last_keyword in ["tu est", "est tu", "est-tu"]:
                    if message.mentions:  # If the list is not empty
                            author = message.mentions[0].nick
                            if author == None:
                                author = message.mentions[0].name
                    else:
                        try:
                            messages = await channel.fetch_message(message.reference.message_id)
                            author = str(messages.author.display_name).lower()
                        except:
                            continue_loop = True
                            async for message_content in channel.history(limit=100):
                                successful_try = False
                                if str(message_content.author.display_name).lower() == str(message.author.display_name).lower():
                                    try:
                                        messages = await channel.fetch_message(message_content.reference.message_id)
                                        author = str(messages.author.display_name).lower()
                                        successful_try = True
                                    except:
                                        author = "someone"
                                else:
                                    author = str(message_content.author.display_name).lower()
                                    break
                                if successful_try:
                                    break
                    if re.sub(r'\W', ' ', author).lower().strip() == re.sub(r'\W', ' ', first_word).lower().strip():
                        await text("oui, ils sont " + author)
                    else:
                        await text("non, ils sont " + author)
                    bot_data.correction_callouts += 1
                elif last_keyword in ["am i"]:
                    if str(message.author.display_name).lower() == re.sub(r'\W', ' ', first_word).lower().strip():
                        await text("yes you're " + str(message.author.display_name).lower())
                    elif not str(first_word).isalnum():
                        await text("you're " + str(message.author.display_name).lower())
                    elif str(message.author.display_name).lower() == "aj_001" and re.sub(r'\W', ' ', first_word).lower().strip() == "aj":
                        await text("yes, you're " + str(message.author.display_name).lower())
                    else:
                        await text("no you're " + str(message.author.display_name).lower())
                    bot_data.correction_callouts += 1
                elif last_keyword == "suis je":
                    await text("no tu es " + str(message.author.display_name).lower())
                    bot_data.correction_callouts += 1
                else:
                    await text(f"hi {cropped_message} \ni'm helen")
                    bot_data.im_callouts += 1

    if message.channel.id == 1208611858001690715 and message.content == str(bot_data.number):
        bot_data.moyais += 1
        try:
            await message.add_reaction("🗿")
        except:
            await asyncio.sleep(5)
            await message.add_reaction("🗿")
        bot_data.number = await send_number(channel, bot_data.number, bot_data.rate_limit)
        await bot.process_commands(message)
        async for message in channel.history(limit=1):
            try:
                await message.add_reaction("🗿")
            except:
                await asyncio.sleep(5)
                await message.add_reaction("🗿")
    elif message.channel.id == 1208611858001690715 and not message.content == str(bot_data.number) and str(message.content).isdigit():
        bot_data.moyais += 1
        try:
            await message.add_reaction("🗿")
        except:
            await asyncio.sleep(5)
            await message.add_reaction("🗿")
        await bot.process_commands(message)
        async for message in channel.history(limit=1):
            try:
                await message.add_reaction("🗿")
            except:
                await asyncio.sleep(5)
                await message.add_reaction("🗿")
    elif message.channel.id == 1208611858001690715:
        bot_data.moyais += 1
        try:
            await message.add_reaction("🗿")
            if (message.content[:(len(str(bot_data.number + 1)))].strip()) == str(bot_data.number + 1):
                bot_data.number = await send_number(channel, bot_data.number, bot_data.rate_limit)
            elif (message.content[:(len(str(bot_data.number+1)))].strip()).isdigit() and not (message.content[:(len(str(bot_data.number+1)))].strip()) == str(bot_data.number):
                print(bot_data.number)
            async for message in channel.history(limit=2):
                await message.add_reaction("🗿")
                await asyncio.sleep(0.3) # Not needed just here to limit ratelimits
        except:
            await asyncio.sleep(5)
            await message.add_reaction("🗿")
            async for message in channel.history(limit=2):
                await message.add_reaction("🗿")
                await asyncio.sleep(0.3) # Not needed just here to limit ratelimits    
bot.run('Discord-API-Key')
