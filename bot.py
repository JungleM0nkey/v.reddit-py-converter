import os
import discord 
from discord.ext import commands
import requests, urllib, json, time
import asyncio

TOKEN = os.getenv('DISCORD_TOKEN')
IMGUR_CLIENT = os.getenv('IMGUR_CLIENT')
#client = discord.Client()
bot = commands.Bot(command_prefix='!')

def convert(reddit_link):
    #if the link is a v.redd.it link convert it to the full url
    reddit_link = requests.get(reddit_link)
    reddit_link = reddit_link.url
    #download the video from reddit
    if reddit_link[-1] != r'/':
        reddit_link = reddit_link + '/.json'
    else:
        reddit_link = reddit_link + '.json'
    r = requests.get(reddit_link, headers = {'User-agent': 'v.reddit-py 1.0'})
    json_data = r.json()
    #this checks if the link actually contains a v.redd.it video
    try:
        fallback_url = json_data[0]['data']['children'][0]['data']['secure_media']['reddit_video']['fallback_url']
        print(f'Downloading video from: {fallback_url}')
        urllib.request.urlretrieve(fallback_url, "download.mp4")
        #upload the video to imgur
        imgur_url = "https://api.imgur.com/3/upload"
        payload = {'type': 'file','disable_audio': '0','title':'test'}
        files = [('video', open('download.mp4','rb'))]
        headers = {'Authorization': 'Client-ID '+IMGUR_CLIENT}
        print('Uploading to imgur')
        response = requests.request("POST", imgur_url, headers=headers, data = payload, files = files)
        print(response)
        json_data = json.loads(response.text)
        print(response.text.encode('utf8'))
        upload_link = json_data['data']['link']
        upload_id = json_data['data']['id']
        status_code = json_data['status']
        print(f'Upload done')
        return (upload_link, upload_id, status_code)
    except TypeError:
        upload_link = None
        upload_id = None
        status_code = 404
        return (upload_link, upload_id, status_code)

    

def fetch(upload_id):
    print(f'Checking processing status for id: {upload_id}')
    imgur_url = f"https://api.imgur.com/3/image/{upload_id}"
    headers = {'Authorization': 'Client-ID '+IMGUR_CLIENT}
    response = requests.request("GET", imgur_url, headers=headers)
    json_data = json.loads(response.text)
    processing_status = json_data['data']['processing']['status']
    return processing_status

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
    message = await ctx.send(f'⏱Converting...')
    upload_link, upload_id, status_code = convert(link)
    if status_code == 200:
        processing_status = fetch(upload_id)
        while processing_status != 'completed':
            time.sleep(2)
            processing_status = fetch(upload_id)
        print(f'Processing finished, posting: {upload_link}')
        await message.edit(content=f"{upload_link}")
    else:
        await message.edit(content=f'Error status code: {status_code}')
    #await asyncio.sleep(5)  
    #await message.edit(content=f"{response}")
    #with open(response, 'rb') as fp:
    #    await ctx.send(file=discord.File(fp))


#bot.add_command(convert_link)
bot.run(TOKEN)