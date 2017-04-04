from api_collection import *


file=Youtube.download(video_id="H4JEkZgI4gU", download_folder="/home/aswasif007/Desktop")

# print file

keywords=['hacking', 'ethical', 'attack', 'denial', 'service']
temp="/home/aswasif007/Desktop/snapshots"

Video.extract_frames(file, folder=temp)
# Video.eliminate_irrelevants(folder="/home/aswasif007/Desktop/snapshots")

# words=Frame.extract_words(file)
# for w in  words:
# 	if(w in keywords):
# 		print w