import discord
import asyncio
import datetime

from discord.ext import commands
from jasper import db

class utilities(commands.Cog):

    def __init__(self, client):
        self.client = client
        
    def isitdev(ctx):
        return ctx.author.id == 524001661379936268 or ctx.author.id == 512804342445899787

    def listToString(self, s):
        string = ''
        return (string.join(s))

    task = db["Tasks"]

#Polls
    @commands.command(aliases = ['vote'])
    @commands.has_role('Staff')
    async def poll(self, ctx, *, question):
        await ctx.message.delete()
        channel = self.client.get_channel(823041499259207690)
        date = datetime.datetime.now()
        options = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth']
        answers = ['', '', '', '', '', '', '', '', '', '']
        choices = ['', '', '', '', '', '', '', '', '', '']
        emojis = ['\U0001F1E6', '\U0001F1E7', '\U0001F1E8', '\U0001F1E9', '\U0001F1EA', '\U0001F1EB', '\U0001F1EC', '\U0001F1ED', '\U0001F1EE', '\U0001F1EF']
        pollNum = self.task.find({"_id": "Poll"})
        for x in pollNum:
            num = int(x["number"])
        num += 1
        embed = discord.Embed(title = f'__Poll #{num}__ ', color = 0xFFCB00)
        embed.set_author(name = ctx.author, icon_url = ctx.author.avatar_url)
        embed.set_footer(text = f'{date:%B %d, %Y} at {date:%H:%M} EST', icon_url = 'https://cdn.discordapp.com/attachments/818494514867077144/844009816577146900/ghost.jpg')
        embed2 = discord.Embed(title = 'There is a minimum of 2 options and a maximum of 10 options', color = 0xFFCB00)
        instructions = await ctx.send(embed = embed2)
        for x in range(10):
            input = await ctx.send(f'What is the {options[x]} response option? Type `Done` when you have typed in all options or `Exit` if you do not wish to continue')
            try:
                send = True
                answers[x] = await ctx.bot.wait_for('message', check = lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout = 30)
                await input.delete()
                if answers[x].content.lower() == 'done':
                    await answers[x].delete()
                    if x == 0:
                        await ctx.send('You have entered no options, please restart and enter more')
                        send = False
                        break
                    elif x == 1:
                        await ctx.send('You have only entered one option, please restart and enter more')
                        send = False
                        break
                    total = x
                    break
                elif answers[x].content.lower() == 'exit':
                    await answers[x].delete()
                    send = False
                    break
                await answers[x].delete()
                #Custom Emote for Reactions
                cemote = await ctx.send('What emoji are you using for this option? Type `Done` to use the default emote or `Exit` if you do not wish to continue')
                try:
                    emote = await ctx.bot.wait_for('message', check = lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout = 20)
                    await cemote.delete()
                    try:
                        await emote.add_reaction(emote.content)
                        emojis[x] = emote.content
                        await emote.delete()
                    except discord.errors.HTTPException:
                        if emote.content.lower() == 'done':
                            await emote.delete()
                        elif emote.content.lower() == 'exit':
                            await emote.delete()
                            send = False
                            break
                        else:
                            await emote.delete()
                            await ctx.send('Invalid Emote: You are either sending an emote from another server or it does not exist. Default emote will be used', delete_after = 5.0)
                except asyncio.TimeoutError:
                    await cemote.delete()
                    await ctx.send('Default emote will be used', delete_after = 3.0)
                total = 10
            except asyncio.TimeoutError:
                await input.delete()
                send = False
                await ctx.send('You took too long to type the answer, please restart')
                break
        await instructions.delete()
        #Attachments for Embed
        if send == True:
            attachment = await ctx.send('What image would you like to add? Type `Done` to have no images or `Exit` if you do not wish to continue')
            try:
                image = await ctx.bot.wait_for('message', check = lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout = 60)
                await attachment.delete()
                try:
                    embed.set_image(url = image.attachments[0].url)
                    await image.delete()
                except IndexError:
                    if image.content.lower() == 'done':
                        await image.delete()
                    elif image.content.lower() == 'exit':
                        await image.delete()
                        send = False
                    else:
                        await image.delete()
            except asyncio.TimeoutError:
                await attachment.delete()
        if send == True:
            try:
                for x in range(total):
                    choices[x] = (f'{emojis[x]}: {answers[x].content}\n')
                embed.add_field(name = f'Question: {question}', value = self.listToString(choices), inline = False)
                msg = await channel.send(embed = embed)
                self.task.update_one({"_id": "Poll"}, {"$set":{"number": num}})
                for x in range(total):
                    await msg.add_reaction(emojis[x])
            except AttributeError:
                pass

    @poll.error
    async def poll_error(self, ctx, error):
        await ctx.message.delete()
        if isinstance(error, commands.MissingRole):
            await ctx.send('You are missing the Staff Role', delete_after = 5.0)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Please use this format: `!poll (Question)`', delete_after = 5.0)

#Ping Latency
    @commands.command(aliases = ['pong'])
    @commands.cooldown(1, 3.0, commands.BucketType.user)
    async def ping(self, ctx):
        await ctx.message.delete()
        ping = int(round(self.client.latency * 1000))
        embed = discord.Embed(title = ':ping_pong: Ping Latency :ping_pong:', color = 0xFFCB00)
        if ctx.message.content == '!ping':
            name = 'Pong!'
        elif ctx.message.content == '!pong':
            name = 'Ping!'
        embed.add_field(name = name, value = f'The latency is {ping} ms', inline = True)
        await ctx.send(embed = embed)
    
    @ping.error
    async def ping_error(self, ctx, error):
        await ctx.message.delete()
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f'You are on cooldown! Try again in {error.retry_after:.2f}s', delete_after = 5.0)

#Make a role temporarily pingable
    @commands.command()
    @commands.has_role('Staff')
    async def roleping(self, ctx, duration: int, *, role: commands.RoleConverter):
        await ctx.message.delete()
        privatechannels = ['700600677596004415', '847873556725628998', '745331414718742569', '701877914001735772']
        if ctx.message.channel.id in privatechannels:
            if duration <= 45 and duration > 0:
                role.edit(mentionable = True)
                await ctx.send(f'{role.name} will be pingable for the next {duration} seconds')
                asyncio.sleep(duration)
                role.edit(mentionable = False)
            else:
                await ctx.send('Duration must be between 0-45 seconds')
        else:
            await ctx.send('You can not use this command here')

    @roleping.error
    async def roleping_error(self, ctx, error):
        await ctx.message.delete()
        if isinstance(error, commands.MissingRole):
            await ctx.send('Please use this format: `!roleping (Time) (Role)`', delete_after = 5.0)
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send('You are missing the Staff Role', delete_after = 5.0)

#Emergency Staff Ping
    def isitthem(ctx):
        return ctx.author.id == 772266273492041728 or ctx.author.id == 629807496210415655 or ctx.author.id == 498176822404579330 or ctx.author.id == 479411003881160707 or ctx.author.id == 226457061959925761 or ctx.author.id == 325790134601646080

    @commands.command(aliases = ['sos'])
    @commands.check(isitthem)
    async def emergency(self, ctx):
        await ctx.message.delete()
        msg = await ctx.send(f'Are you sure you want to ping Staff?')
        await msg.add_reaction('\U00002714')
        await msg.add_reaction('\U00002716')
        try:
            reaction, user = await ctx.bot.wait_for('reaction_add', check = lambda r, u: u == ctx.author and str(r.emoji) in ('\U00002714','\U00002716'), timeout = 30)
            if str(reaction.emoji) == '\U00002714':
                await ctx.send(f'<@&779814865371004948>')
            elif str(reaction.emoji) == '\U00002716':
                await ctx.send("Ok, please don't try this again unless it's an emergency", delete_after = 5.0)
        except asyncio.TimeoutError:
            await ctx.send(f'Timed Out')
            return

    @emergency.error
    async def emergency_error(self, ctx, error):
        await ctx.message.delete()
        if isinstance(error, commands.CheckFailure):
            pass

#Identification Redirect
    @commands.command(aliases = ['identification'])
    async def id(self, ctx):
        await ctx.message.delete()
        await ctx.send(f'Please go to <#700563120690561024> to identify yourself!')

#Charles' PG Warning
    @commands.command()
    async def pg(self, ctx):
        await ctx.message.delete()
        await ctx.send(f'**PLEASE KEEP IT HECCING PG**')

#School Talk Redirect
    @commands.command(aliases = ['schooltalk'])
    async def st(self, ctx):
        await ctx.message.delete()
        await ctx.send(f'Please go to <#771694740521091114> for school talk!')

#General Redirect
    @commands.command(aliases = ['general'])
    async def gen(self, ctx):
        await ctx.message.delete()
        await ctx.send(f'Please go to <#760284361814835200> for your conversation!')

#Bot Commands Redirect
    @commands.command(aliases = ['botcommands'])
    async def bc(self, ctx):
        await ctx.message.delete()
        await ctx.send(f'Please go to <#789619349903507456> for bot commands!')

#Wonger's Shitpost Redirect
    @commands.command()
    async def meme(self, ctx):
        await ctx.message.delete()
        await ctx.send(f"Please send these to <#760284416848298025> so you don't clog up this chat!")

def setup(client):
    client.add_cog(utilities(client))