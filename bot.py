#!/usr/bin/python3 -u
import os
import shutil
import discord 
from discord.ext import commands
import requests, urllib, json, time
import asyncio
import random
import string
import ffmpeg
import subprocess
import requests

TOKEN = os.getenv('DISCORD_TOKEN')
#IMGUR_CLIENT = os.getenv('IMGUR_CLIENT')
DOWNLOADS_DIR = os.getenv('DOWNLOADS_DIR')
WORKING_DIR = os.getenv('WORKING_DIR') or os.getcwd()
STREAMABLE_EMAIL = os.getenv('STREAMABLE_EMAIL')
STREAMABLE_PW = os.getenv('STREAMABLE_PW')
#client = discord.Client()
bot = commands.Bot(command_prefix='!')

def randomString(stringLength=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

#saves previously existing video in the downloads folder
def archive():
    #archive the previous download if there was one
    os.chdir(WORKING_DIR)
    if os.path.exists(f'{WORKING_DIR}/download.mp4'):
        print('Archiving previous video')
        new_name = randomString(12)
        #create the downloads folder if it doesnt exist
        if not os.path.exists(DOWNLOADS_DIR):
            os.mkdir(DOWNLOADS_DIR)
        #rename the previous download and move it to the downloads folder
        shutil.move(f"{WORKING_DIR}/download.mp4", f"{DOWNLOADS_DIR}/{new_name}.mp4")

#merges audio and video
#def merge():
#    video = ffmpeg.input(f'{WORKING_DIR}/download_video.mp4')
#    audio = ffmpeg.input(f'{WORKING_DIR}/download_audio.mp4')
#    out = ffmpeg.output(video, audio, f'{WORKING_DIR}/download.mp4', vcodec='copy', acodec='aac', strict='experimental')
#    out.run()
    #cleanup
#    os.remove(f'{WORKING_DIR}/download_video.mp4')
#    os.remove(f'{WORKING_DIR}/download_audio.mp4')

#main convert function for reddit links to imgur links
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
    dash_url = json_data[0]['data']['children'][0]['data']['secure_media']['reddit_video']['dash_url']
    dash_url = dash_url.split('?')[0]
    post_title = json_data[0]['data']['children'][0]['data']['title']
    #download video
    print(f'Downloading video from: {dash_url}')
    subprocess.run(['ffmpeg', '-i', dash_url, '-c', 'copy', f'{post_title}.mp4'])
    print(f"Download of {post_title} finished, starting video upload to Streamable")
    file_name = f"{post_title}.mp4"
    #upload video to streamable
    video_file= {'file': (file_name, open(file_name, 'rb'))}
    upload_request = requests.post('https://api.streamable.com/upload', auth=(STREAMABLE_EMAIL, STREAMABLE_PW), files=video_file).json()
    print(upload_request)
    upload_info = requests.get('https://api.streamable.com/videos/'+str(upload_request['shortcode']), auth=(STREAMABLE_EMAIL, STREAMABLE_PW)).json()
    print(upload_info)
    status_code = upload_info['status']
    #urllib.request.urlretrieve(fallback_url, "download.mp4")
    #download audio
    #print(f'Downloading audio from: {audio_url}')
    #urllib.request.urlretrieve(audio_url, "download_audio.mp4")
    #merge audio and video
    #merge()
    #upload the video to imgur
    #imgur_url = "https://api.imgur.com/3/upload"
    #payload = {'type': 'file','disable_audio': '0','title':'test'}
    #files = [('video', open('download.mp4','rb'))]
    #headers = {'Authorization': 'Client-ID '+IMGUR_CLIENT}
    #print('Uploading to imgur')
    #response = requests.request("POST", imgur_url, headers=headers, data = payload, files = files)
    #print(response)
    #json_data = json.loads(response.text)
    #print(response.text.encode('utf8'))
    #status_code = json_data['status']
    if status_code != 1:
        upload_error = upload_info['message']
        upload_link = None
        #upload_id = None
        print(f'Error Uploading: {upload_error}')
    else:
        upload_error = None
        upload_link = "https://"+upload_info['url']
        #upload_id = json_data['data']['id']
        print(f'Upload done')
    return (upload_link, status_code, upload_error)

    

#def fetch(upload_id):
#    print(f'Checking processing status for id: {upload_id}')
#    imgur_url = f"https://api.imgur.com/3/image/{upload_id}"
#    headers = {'Authorization': 'Client-ID '+IMGUR_CLIENT}
#    response = requests.request("GET", imgur_url, headers=headers)
#    json_data = json.loads(response.text)
#    processing_status = json_data['data']['processing']['status']
#    return processing_status

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
            upload_link, status_code, upload_error = convert(link)
            if status_code == 1:
                #processing_status = fetch(upload_id)
                #while processing_status != 'completed':
                #    time.sleep(2)
                #    processing_status = fetch(upload_id)
                time.sleep(10)
                print(f'Processing finished, posting: {upload_link}')
                await message.edit(content=f"{upload_link}")
            else:
                await message.edit(content=f'Error {status_code}: {upload_error}')
        except Exception as e:
            print(f'Ignoring link: {e}')
            pass
        
    
@bot.command(name='c')
async def convert_link(ctx, link: str):
    print(f'Converting link: {link}')
    archive()
    message = await ctx.send(f'⏱Converting...')
    upload_link, status_code, upload_error = convert(link)
    if status_code == 1:
        #processing_status = fetch(upload_id)
        #while processing_status != 'completed':
        #    time.sleep(2)
        #    processing_status = fetch(upload_id)
        time.sleep(10)
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