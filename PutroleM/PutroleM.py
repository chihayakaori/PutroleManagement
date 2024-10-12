import discord
import yaml
import datetime
import os
import MyFunctions
from discord.ext import commands, tasks
from ComEv import Commands, Events


intents = discord.Intents.all()
intents.dm_messages = True
client = commands.Bot(command_prefix='$', intents=intents)


coms = Commands(client)
ev = Events(client)


@client.event
async def on_ready():
    print("I'm ready !")
    await exp_date()
    send_today_date.start()
    check_changes.start()


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return  
    raise error  


with open('Settings.yaml', 'r') as file:
    Settings = yaml.safe_load(file)


@tasks.loop(seconds=10)
async def check_changes():
    Settings = MyFunctions.reload_settings()
    Exp0 = int(Settings.get('exp set')) 
    Exp1 = int(Settings.get('exp')) 
    if Exp0 != Exp1:
        with open('Settings.yaml', 'r') as file:
            Settings = yaml.safe_load(file)
        if 'expirate date' in Settings:
            del Settings['expirate date']
        with open('Settings.yaml', 'w') as file:
            yaml.dump(Settings, file)
        await exp_date()


@tasks.loop(seconds=10)
async def send_today_date():
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    await check_date(today)
    

async def exp_date():
    Settings = MyFunctions.reload_settings()
    if 'expirate date' in Settings:
        return
    else: 
        today = datetime.datetime.now()
        Settings = MyFunctions.reload_settings()
        Exp = int(Settings.get('exp')) 
        Ndate = today + datetime.timedelta(days=Exp)
        Settings['expirate date'] = Ndate.strftime('%Y-%m-%d')
        Settings['exp set'] = Exp
        with open('Settings.yaml', 'w') as file:
            yaml.dump(Settings, file)


async def check_date(today):
    Settings = MyFunctions.reload_settings()
    expirate_date = Settings.get('expirate date')
    if today >= expirate_date:
        MyFunctions.remove_passwords_from_yaml_file('Settings.yaml')
        guild_id = Settings.get('guild_id')
        role_id = Settings.get('role_id')
        guild = client.get_guild(guild_id)
        role = discord.utils.get(guild.roles, id=role_id)
        MyFunctions.remove_expirate_date()
        await exp_date()
        for member in guild.members:
            if role in member.roles:
                embed = discord.Embed(
                title="Warning",
                description= "Your subscription has ended. Please redo the @sub command and enter a new code to regain the role.",
                color=discord.Color.red()
                )
                await member.send(embed=embed)
                await member.remove_roles(role)
                if os.path.exists('Log.txt'):
                    os.remove('Log.txt')
                else:
                    print("An issue occurred with deleting the file Log.txt. Was already non-existent.")


@client.event
async def on_message(message):
    await ev.on_message(message)


@client.command(name='set')
async def set(ctx, *, passwords=None):
    await coms.set(ctx, passwords=passwords)


@client.command(name='sub')
async def sub(ctx, *, password=None):
    await coms.sub(ctx, password=password)


@client.command(name='clear')
async def clear(ctx, *message_ids: int):
    await coms.clear(ctx, *message_ids)


Token = Settings.get('Tk')
client.run(Token)

