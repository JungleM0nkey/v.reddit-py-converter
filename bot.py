import os
import discord 
from discord.ext import commands
import requests, urllib, json, time
import asyncio
import random
import string

TOKEN = os.getenv('DISCORD_TOKEN')
IMGUR_CLIENT = os.getenv('IMGUR_CLIENT')
#client = discord.Client()
bot = commands.Bot(command_prefix='!')

def randomString(stringLength=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def archive():
    #archive the previous download if there was one
    if os.path.exists('download.mp4'):
        new_name = randomString(12)
        #create the downloads folder if it doesnt exist
        if not os.path.exists('downloads'):
            os.mkdir('downloads')
        #rename the previous download and move it to the downloads folder
        os.rename("download.mp4", f"downloads/{new_name}.mp4")

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
        status_code = json_data['status']
        if status_code != 200:
            upload_error = json_data['data']['error']
            upload_link = None
            upload_id = None
            print(f'Error Uploading: {upload_error}')
        else:
            upload_error = None
            upload_link = json_data['data']['link']
            upload_id = json_data['data']['id']
            print(f'Upload done')
        return (upload_link, upload_id, status_code, upload_error)
    except TypeError:
        upload_error = 'Wrong link type'
        upload_link = None
        upload_id = None
        status_code = 400
        return (upload_link, upload_id, status_code, upload_error)

    

def fetch(upload_id):
    print(f'Checking processing status for id: {upload_id}')
    imgur_url = f"https://api.imgur.com/3/image/{upload_id}"
    headers = {'Authorization': 'Client-ID '+IMGUR_CLIENT}
    response = requests.request("GET", imgur_url, headers=headers)
    json_data = json.loads(response.text)
    processing_status = json_data['data']['processing']['status']
    return processing_status

@bot.event
async def on_ready():
    print(f'{bot.user} is connected and ready.')


#this removes the need for !c before v.redd.it video links. The bot will actively convert them as they get posted
@bot.event
async def on_message(message):
    await bot.process_commands(message)
    #lets not do an infinite loop
    if message.author == bot.user:
        return   
    if message.content.startswith('https://www.reddit.com/r/') or message.content.startswith('https://v.redd.it/'):
        link = message.content.split(' ')[0] #if there is any spaces in the msg make sure to grab the link only
        #check if reddit link contains a video
        #if the link is a v.redd.it link convert it to the full url
        reddit_link = requests.get(link)
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
            archive()
            message = await message.channel.send(f'⏱Converting...')
            upload_link, upload_id, status_code, upload_error = convert(link)
            if status_code == 200:
                processing_status = fetch(upload_id)
                while processing_status != 'completed':
                    time.sleep(2)
                    processing_status = fetch(upload_id)
                print(f'Processing finished, posting: {upload_link}')
                await message.edit(content=f"{upload_link}")
            else:
                await message.edit(content=f'Error {status_code}: {upload_error}')
        except:
            print('Ignoring link')
            pass
        
    
@bot.command(name='c')
async def convert_link(ctx, link: str):
    print(f'Converting link: {link}')
    archive()
    message = await ctx.send(f'⏱Converting...')
    upload_link, upload_id, status_code, upload_error = convert(link)
    if status_code == 200:
        processing_status = fetch(upload_id)
        while processing_status != 'completed':
            time.sleep(2)
            processing_status = fetch(upload_id)
        print(f'Processing finished, posting: {upload_link}')
        await message.edit(content=f"{upload_link}")
    else:
        await message.edit(content=f'Error {status_code}: {upload_error}')
    #await asyncio.sleep(5)  
    #await message.edit(content=f"{response}")
    #with open(response, 'rb') as fp:
    #    await ctx.send(file=discord.File(fp))


#bot.add_command(convert_link)
bot.run(TOKEN)