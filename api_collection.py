from pytube import YouTube
from apiclient.discovery import build
from oauth2client.tools import argparser
from itertools import izip
import os, shutil, urllib, cv2, Image

class Youtube:
	@staticmethod
	def download(video_id, download_folder="/tmp/"):
		try:
			yt=YouTube("https://www.youtube.com/watch?v="+video_id)
			print "Downloading file: "+yt.filename
			video=yt.filter('mp4')[-1]
			video.download(download_folder)
			print "Download completed."

			return os.path.join(download_folder, yt.filename)
		except OSError, e:
			print "File already exists."
			return os.path.join(download_folder, yt.filename)
		except:
			print "An error has occurred."
	###

	@staticmethod
	def search(search_term, max_results=25):
		DEVELOPER_KEY="AIzaSyAyXI7PZSzjmE5luCjhr8q01l1JO7hcxFk"
		YOUTUBE_API_SERVICE_NAME="youtube"
		YOUTUBE_API_VERSION="v3"

		def youtube_search(options):
			youtube=build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

			# Call the search.list method to retrieve results matching the specified query term.
			search_response=youtube.search().list(q=options.q, part="id,snippet", maxResults=options.max_results).execute()

			videos=[]

			# Add each result to the appropriate list, and then display the lists of
			# matching videos, channels, and playlists.
			for search_result in search_response.get("items", []):
				if(search_result["id"]["kind"]=="youtube#video"):
					videos.append(search_result["id"]["videoId"])

			return videos
		###

		argparser.add_argument("--q", help="Search term", default=search_term)
		argparser.add_argument("--max-results", help="Max results", default=max_results)
		args = argparser.parse_args()

		try:
			return youtube_search(args)
		except HttpError, e:
			print "An error occured."
	###
###

class Video:
	@staticmethod
	def eliminate_irrelevants(folder="/tmp/snapshots"):
		def img_compare(img_name_1, img_name_2):
			i1 = Image.open(img_name_1)
			i2 = Image.open(img_name_2)
			assert i1.mode == i2.mode, "Different kinds of images."
			assert i1.size == i2.size, "Different sizes."
		 
			pairs = izip(i1.getdata(), i2.getdata())
			if len(i1.getbands()) == 1:
			    # for gray-scale jpegs
			    dif = sum(abs(p1-p2) for p1,p2 in pairs)
			else:
			    dif = sum(abs(c1-c2) for p1,p2 in pairs for c1,c2 in zip(p1,p2))
			 
			ncomponents = i1.size[0] * i1.size[1] * 3
			return (dif / 255.0 * 100) / ncomponents
		###

		onlyfiles = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
		have_to_delete=False
		num_of_imgs = len(onlyfiles)

		for i in range(1, len(onlyfiles)):
			img_name_1 = os.path.join(folder,str(i)+".jpeg") 
			img_name_2 = os.path.join(folder,str(i+1)+".jpeg") 

			print img_name_1 , " , " , img_name_2 , ":" ,img_compare(img_name_1, img_name_2)
			difference = img_compare(img_name_1, img_name_2)

			if(have_to_delete):
				print "Deleting ", last_img_name
				os.remove(last_img_name)

			have_to_delete=bool(difference<=10)
			last_img_name=img_name_2

		if(difference<=10):
			print "Deleting ", last_img_name
			os.remove(last_img_name)
	###

	@staticmethod
	def extract_frames(video_file, folder="/tmp/snapshots/"):
		print "Extracting frames in "+folder

		if(os.path.exists(folder)): shutil.rmtree(folder)
		os.mkdir(folder)

		cap=cv2.VideoCapture(video_file)
		frameRate=cap.get(5)					# frame rate
		count=1

		while(cap.isOpened()):
			frameId=int(frameRate*count)		# current frame number
			cap.set(1,frameId)
			ret,frame=cap.read()

			if(ret is False): break
			filename=os.path.join(folder,"{}.jpeg".format(count))
			cv2.imwrite(filename, frame)
			count+=1

		cap.release()
		print "Extraction completed."

		return folder
	###
###