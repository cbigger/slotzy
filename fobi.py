import os
import random
import discord
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

from discord import Intents
intents = Intents.default()
intents.guilds = True
intents.messages = True
intents.members = True
intents.emojis = True
intents.message_content = True
client = discord.Client(intents=intents)
HubCoin = "<:hubcoin:925179250477256734>"


# Dictionary to store balance
bookie = {}
# The owner of the machine
owner = "815689617134714881"


def add_balance(user, amount):
    user = str(user)  # Ensure user is a string
    if user in bookie:
        bookie[user] += amount
    else:
        bookie[user] = amount

def subtract_balance(user, amount):
    user = str(user)  # Ensure user is a string
    if user in bookie:
        bookie[user] -= amount
    else:
        bookie[user] = -amount  

def get_balance(user):
    user = str(user)  # Ensure user is a string
    if user in bookie:      
        return bookie[user]
    else:
        return 0

def slotCheckBalance(user):
    balance = get_balance(user)
    return f"**Your current balance is {balance} {HubCoin}**"

async def slotCashout(user):
    user = str(user)  # Ensure user is a string
    owner_user = await client.fetch_user(owner)
    total_cashed_out = get_balance(user)
    bookie[user] = 0
    return f"**{owner_user.mention}, {total_cashed_out} {HubCoin} has been cashed out for <@{user}>.\n<@{user}>'s account has been cleared.**"

def slotMachineCommand(num_spins,wager,message):
    outcomes = [':tumbler_glass:', HubCoin, ':skull_crossbones:', ':cherries:']
    winnings = {':tumbler_glass:' : (wager * 18), HubCoin : (wager * 30), ':skull_crossbones:' : wager * 3, ':cherries:' : wager * 9  }

    total_winnings = 0
    total_cost = num_spins * wager
    if (wager == 6) and (num_spins == 1):
        yield "***-kzzt-**...er set: 16...**-kzzt-**...16*"
        wager = 16
        num_spins = 16
    yield f"*wager set: {wager} {HubCoin} per spin*"
    for i in range(num_spins):
        spin_result = [random.choice(outcomes) for k in range(3)]
        spin_result_str = ' | '.join(spin_result)

        if (spin_result[0]==spin_result[1] and spin_result[0]==spin_result[2]) and (spin_result[0] in winnings):
            total_winnings += winnings[spin_result[0]]
            response = f'{spin_result_str}   :tada: **WINNER** :tada: **{winnings[spin_result[0]]}** {HubCoin}'
        else:
            response = f"{spin_result_str}"

        yield response

    total_profit = (total_winnings - total_cost)
    if total_profit < 0:
        subtract_balance(message.author.id, abs(total_profit))
        yield f"**{message.author.mention} YOU LOSE {abs(total_profit)} {HubCoin}**\nYour balance is now **{get_balance(message.author.id)} {HubCoin}**"
    else:
        add_balance(message.author.id, total_profit)    
        yield f"**{message.author.mention} YOU WIN {total_profit} {HubCoin}**\nYour balance is now **{get_balance(message.author.id)} {HubCoin}**"

@client.event
async def on_ready():
    for guild in client.guilds:
        print(f'{client.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})')


@client.event
async def on_message(message):
    print(f"Message from {message.author}: {message.content}")  # Log every message received
    if message.author == client.user:
        print()
        return

    if message.content.lower().startswith('!slot'):
        print("Slot command received")  # Confirm command is recognized


        # Split the message content by spaces and retrieve the number of spins
        split_message = message.content.split(' ')

        # Check if the message has a valid number of spins
        if len(split_message) < 2:
            await message.channel.send(f"{message.author.mention}  Please enter a valid number of **SPINS** (1-10) x your **WAGER** per spin (1-50)" +
                                f"\nExample: `!slot 3 5` will spin 3 times for 5 {HubCoin} each spin, costing you 15 {HubCoin} total."
                               + f"\n{':skull_crossbones:'*3} = **wager** x 3\n{':cherries:'*3} = **wager** x 9\n{':tumbler_glass:'*3} = **wager** x 18\n{HubCoin * 3} = **wager** x 30")

            return

        try:
            num_spins = int(split_message[1])  # Get the number of spins from the message
        except:
            await message.channel.send(f"{message.author.mention} Please enter a valid number of spins: 1-10")
            return

        # Validate the number of spines
        if num_spins < 1 or num_spins > 10:
            await message.channel.send(f"{message.author.mention} Please enter a number between 1 and 10.")
            return

        # Check if the message has a valid wager
        wagers = list(range(0,51))

#            return

        try:
            pot_wager = int(split_message[2])
            if pot_wager in wagers:
                wager = pot_wager        # Get the number of spins from the message
            else:
                await message.channel.send("Please enter a valid wager.")
                return
        except:
            if len(split_message) < 3:
                wager = 5
            else:


                return


        results = []
        for result in slotMachineCommand(num_spins, wager, message):
            await message.channel.send(result)

    elif message.content.lower() == '!balance':
        balance_message = slotCheckBalance(str(message.author.id))
        await message.channel.send(f"{message.author.mention} {balance_message}")

    elif message.content.lower() == '!cashout':
        cashout_message = await slotCashout(str(message.author.id))
        await message.channel.send(cashout_message)

client.run(TOKEN)
