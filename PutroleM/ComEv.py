import discord
import MyFunctions
import yaml


class Events: 
    def __init__(self, client): 
        self.client = client


    async def on_message(self, message):
        if message.author == self.client.user:
            return

        if message.guild is not None:  
            Settings = MyFunctions.reload_settings()
            existing_passwords = Settings.get('Valid passwords', [])
            
            for password in existing_passwords:
                if password in message.content:
                    existing_passwords.remove(password)
                    MyFunctions.update_settings('Valid passwords', existing_passwords)
                    
                    await message.delete()
                    member = message.author
                    embed = discord.Embed(
                    title="Warning",
                    description= f"{member} sent a forbidden password in the server and it has been removed from the list.",
                    color=discord.Color.red()
                    )
                    await message.channel.send(embed=embed)
                    return

        await self.client.process_commands(message)


class Commands:
    def __init__(self, client):
        self.client = client


    async def set(self, ctx, *, passwords=None):
        Settings = MyFunctions.reload_settings()

        Owner_id = Settings.get('Owner_id')
        if ctx.author.id != Owner_id:
            embed = discord.Embed(
                    title="Warning",
                    description= "You are not the owner of the server, you are not authorized to perform this command.",
                    color=discord.Color.red()
                    )
            await ctx.send(embed=embed)
            return
        
        if ctx.guild is not None:
            embed = discord.Embed(
                    title="Warning",
                    description= "This command can only be executed through a private message and only by the guild master.",
                    color=discord.Color.red()
                    )
            await ctx.send(embed=embed)
            await ctx.message.delete()
            return
            
        if passwords is None:
            embed = discord.Embed(
                    title="Warning",
                    description= "Please enter one or more passwords separated by commas followed by your command. Dog, cat, horse",
                    color=discord.Color.red()
                    )
            await ctx.send(embed=embed)
            return
        
        
        password_list = [password.strip() for password in passwords.split(',')]  
        
        existing_passwords = Settings.get('Valid passwords', [])
        duplicate_passwords = [password for password in password_list if password in existing_passwords]
        
        if duplicate_passwords:
            embed = discord.Embed(
                    title="Warning",
                    description= f"The password(s) {', '.join(duplicate_passwords)} is(are) already present in the settings therefore the command is invalid please try again and enter only passwords that are not already in the Settings file.",
                    color=discord.Color.red()
                    )
            await ctx.send(embed=embed)
            new_passwords = None
        else:
            new_passwords = [password for password in password_list if password not in existing_passwords]
            
            Settings['Valid passwords'].extend(new_passwords)
            
            with open('Settings.yaml', 'w') as file:
                yaml.dump(Settings, file)
            
            embed = discord.Embed(
                    title=":white_check_mark:",
                    description= f"The password(s) {', '.join(new_passwords)} has/have been successfully added to the list.",
                    color=discord.Color.blue()
                    )
            await ctx.send(embed=embed)



    async def sub(self, ctx, *, password=None):
        Settings = MyFunctions.reload_settings()
        if isinstance(ctx.channel, discord.DMChannel):
            if password is None:
                embed = discord.Embed(
                title="Warning",
                description= "You did not provide a password.",
                color=discord.Color.red()
                )
                await ctx.send(embed=embed)
            elif password in Settings['Valid passwords']:
                nbt = int(Settings.get('number of attempts')) 
                if nbt > 0:
                    guild_id = Settings.get('guild_id')
                    role_id = Settings.get('role_id')
                    guild = self.client.get_guild(guild_id)
                    member = guild.get_member(ctx.author.id)
                    if member:
                        role = discord.utils.get(guild.roles, id=role_id)
                        if role not in member.roles:
                            await member.add_roles(role)
                            MyFunctions.add_user_to_file(ctx)
                            embed = discord.Embed(
                            title=":white_check_mark:",
                            description= f"The Role {role} have been assigned.",
                            color=discord.Color.blue())
                            await ctx.send(embed=embed)
                            MyFunctions.decrement_attempts()
                        else:
                            embed = discord.Embed(
                            title="Warning",
                            description= f"You already have the role {role}.",
                            color=discord.Color.red())
                            await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(
                    title="Warning",
                    description="The password has reached its usage limit.",
                    color=discord.Color.red())
                    await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                title="Warning",
                description="The entered password is incorrect.",
                color=discord.Color.red())
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
            title="Warning",
            description="This command must be used in a private message.",
            color=discord.Color.red())
            await ctx.send(embed=embed)
            

    async def clear(self, ctx):
        async for message in ctx.history():
            if message.author == self.client.user:
                await message.delete()    