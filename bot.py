import requests, urllib, json

#download the video
link = input('V.Reddit link please: ')
link = link + '.json'
r = requests.get(link, headers = {'User-agent': 'v.reddit-py-bot 1.0'})
json_data = r.json()
fallback_url = json_data[0]['data']['children'][0]['data']['secure_media']['reddit_video']['fallback_url']
print(f'Downloading video from: {fallback_url}')
urllib.request.urlretrieve(fallback_url, "download.mp4")

#upload the video to imgur
imgur_url = "https://api.imgur.com/3/upload"
payload = {'album': 'ALBUMID',
'type': 'file',
'disable_audio': '0'}
files = [
  ('video', open('download.mp4','rb'))
]
headers = {
  'Authorization': 'Bearer BEARERTOKENHERE'
}
print('Uploading to imgur')
response = requests.request("POST", imgur_url, headers=headers, data = payload, files = files)
json_data = json.loads(response.text)
link = json_data['data']['link']
#link = response.text.encode('utf8')
print('Imgur link: '+link)

