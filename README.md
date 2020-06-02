### Convert v.reddit links to imgur links inside Discord!

Setup:
1. pip install -r requirements.txt
2. apt install ffmpeg
3. add the bot to your Discord server.
4. configure the IMGUR_CLIENT, DISCORD_TOKEN and DOWNLOADS_DIR environment variables
5. run bot.py


Usage:
!c <v.reddit link>

Alternate usage:
The bot will check new messages if they are reddit links with a video and convert automatically without the need for a !c command