import os
import discord 
from discord.ext import commands
import requests, urllib, json, time

TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()
bot = commands.Bot(command_prefix='!')

def convert(reddit_link):
    #download the video from reddit
    if reddit_link[-1] != r'/':
        reddit_link = reddit_link + '/.json'
    else:
        reddit_link = reddit_link + '.json'
    r = requests.get(reddit_link, headers = {'User-agent': 'v.reddit-py 1.0'})
    json_data = r.json()
    fallback_url = json_data[0]['data']['children'][0]['data']['secure_media']['reddit_video']['fallback_url']
    print(f'Downloading video from: {fallback_url}')
    urllib.request.urlretrieve(fallback_url, "download.mp4")
    #upload the video to imgur
    imgur_url = "https://api.imgur.com/3/upload"
    payload = {'type': 'file','disable_audio': '0','title':'test'}
    files = [('video', open('download.mp4','rb'))]
    headers = {'Authorization': 'Client-ID 6cff0087a2d10ca'}
    print('Uploading to imgur')
    response = requests.request("POST", imgur_url, headers=headers, data = payload, files = files)
    print(response)
    json_data = json.loads(response.text)
    #print(json_data)
    link = json_data['data']['link']
    print(f'Posting imgur link: {link}')
    #return 'download.mp4'
    return link

@client.event
async def on_ready():
    print(f'{client.user} is connected and ready.')

#@client.event
#async def on_message(message):
    #lets not do an infinite loop ok?
#    if message.author == client.user:
#        return
    
#    if message.content == '$r':
#        response = 'Usage: $r <v.reddit link>'
#        await message.channel.send(response)
    
@bot.command(name='c')
async def convert_link(ctx, link: str):
    print(f'Converting link: {link}')
    response = convert(link)
    time.sleep(10) #this is here so that imgur doesnt spit out a broke embeded image
    await ctx.send(response)
    #with open(response, 'rb') as fp:
    #    await ctx.send(file=discord.File(fp))


#bot.add_command(convert_link)
bot.run(TOKEN)