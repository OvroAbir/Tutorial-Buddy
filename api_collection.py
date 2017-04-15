from pytube import YouTube
from apiclient.discovery import build
from oauth2client.tools import argparser
from itertools import izip
from PIL import Image,ImageFilter
import os, shutil, urllib, cv2, pytesseract as tess, pysrt

import speech_recognition as sr
import subprocess, ffmpy, glob, os.path
from pydub import AudioSegment

from weighted_levenshtein import lev
import numpy as np

class Youtube:
	@staticmethod
	def download(video_id, download_folder="/tmp/"):
		try:
			yt=YouTube("https://www.youtube.com/watch?v="+video_id)
			print "Downloading file: "+yt.filename
			video=yt.filter('mp4')[-1]
			video.download(download_folder)
			print "Download completed."

			return os.path.join(download_folder, yt.filename+'.mp4')
		except OSError, e:
			print "File already exists."
			return os.path.join(download_folder, yt.filename+'.mp4')
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

	@staticmethod
	def convert_to_srt(video_id):
		srt_name = video_id + '.en.srt'
		vtt_name = video_id + '.en.vtt'
		ass_name = video_id + '.en.ass'

		if(os.path.isfile(srt_name)):
			return srt_name
		
		current_name = ''
		if(os.path.isfile(vtt_name)):
			current_name = vtt_name
		elif(os.path.isfile(ass_name)):
			current_name = ass_name

		inputs = {current_name:None}
		outputs = {srt_name:None}
		ff = ffmpy.FFmpeg(inputs=inputs, outputs=outputs)
		ff.run()

		os.remove(current_name)

		return srt_name
	###

	@staticmethod
	def download_subtitle(video_id):
		v_url = 'https://www.youtube.com/watch?v='+video_id
		command = 'youtube-dl -o "%(id)s" --write-sub --write-auto-sub --sub-lang en --sub-format srt --convert-subs srt --skip-download ' + v_url
		subprocess.call(command, shell=True)

		return Youtube.convert_to_srt(video_id)
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

		last_saved=os.path.join(folder,str(1)+".jpeg")

		for i in range(2, len(onlyfiles)):
			img_name_1 = os.path.join(folder,str(i)+".jpeg") 

			difference = img_compare(img_name_1, last_saved)
			print img_name_1 , " , " , last_saved , ":" ,difference

			if(difference<=2):
				print "Deleting ", img_name_1
				os.remove(img_name_1)
			else:
				last_saved=img_name_1
	###

	@staticmethod
	def extract_frames(video_file, folder="/tmp/snapshots/"):
		print "Extracting frames in "+folder

		if(os.path.exists(folder)): shutil.rmtree(folder)
		os.mkdir(folder)

		cap=cv2.VideoCapture(video_file)
		frameRate=cap.get(5)					# frame rate
		count=0
		nm=1

		print cap.get(7)
	

		while(cap.isOpened()):
			frameId=int(frameRate*count)		# current frame number
			# cap.set(1,frameId)
			ret,frame=cap.read()

			if(ret is False): break

			if(count%int(frameRate)==0):
				filename=os.path.join(folder,"{}.jpeg".format(nm))
				cv2.imwrite(filename, frame)
				nm+=1

			count+=1

		cap.release()

		print "Extraction completed."
		return folder
	###
###


class Frame:
	@staticmethod
	def prepare_img_for_ocr(img_location):
		img = Image.open(img_location)
		width, height = img.size
		if(width < 1366 or height < 768):
			target_ratio = max(1366/width, 768/height)
			img = img.resize((width*target_ratio, height*target_ratio), Image.ANTIALIAS)
		img = img.filter(ImageFilter.SHARPEN)
		img = img.save(img_location, dpi=(350, 350))
	###

	@staticmethod
	def extract_words(img_location):
		Frame.prepare_img_for_ocr(img_location)
		img = Image.open(img_location)
		raw=tess.image_to_string(img)
		return raw.lower().split()
	###

	@staticmethod
	def get_matched_snapshots(folder, keywords):
		matched_img_names = []
		img_names = glob.glob(folder + '/*.jpeg')
		for img_name in img_names:
			words = Frame.extract_words(img_name)
			for keyword in keywords:
				if(WordDistance.iskeyword_in_wordlist(keyword, words) and img_name not in matched_img_names):
					matched_img_names.append(img_name)
		return matched_img_names
	###
###


class Subtitle:
	@staticmethod
	def get_matched_subs(subs, keywords):
		matched_subs = []
		for i in range(0, len(subs)):
			sub = subs[i]
			text = sub.text
			for kw in keywords:
				if(kw in sub.text):
					matched_subs.append(sub)
		return matched_subs
	###

	@staticmethod
	def print_subs(subs):
		for i in range(0, len(subs)):
			sub = subs[i]
			start_time = str(sub.start.hours) + '.' + str(sub.start.minutes) + '.' + str(sub.start.seconds)
			end_time = str(sub.end.hours) + '.' + str(sub.end.minutes) + '.' + str(sub.end.seconds)
			print '[' + start_time +'] ' + sub.text + '[' + end_time +'] '
	###
###


class Audio:
	BING_KEY = "e6a333fe4c364e35b464893e5f9a7320" 
	WIT_AI_KEY = "PMXQI5BPL4M2MN5LG5RDVDSLSGR4RB5Q"

	@staticmethod
	def get_text_from_part_audio_BING(audio_file_name):
		if(not os.path.isfile(audio_file_name)):
			return ' '

		r = sr.Recognizer()
		with sr.AudioFile(audio_file_name) as source:
			audio = r.record(source)
		result = ' '

		try:
			result = r.recognize_bing(audio, key=Audio.BING_KEY)
		except sr.UnknownValueError:
			result = ' '
			print("Microsoft Bing Voice Recognition could not understand audio in " + audio_file_name)
		except sr.RequestError as e:
			result = ' '
			print("Could not request results from Microsoft Bing Voice Recognition service; {0}".format(e))
			print("For file : " + audio_file_name)

		return result
	###

	@staticmethod
	def get_text_from_part_audio_WIT(audio_file_name):
		if(not os.path.isfile(audio_file_name)):
			return ' '
		r = sr.Recognizer()
		with sr.AudioFile(audio_file_name) as source:
			audio = r.record(source)
		result = ' '

		try:
		    result = r.recognize_wit(audio, key=Audio.WIT_AI_KEY)
		except sr.UnknownValueError:
			result = ' '
			print("Wit.ai could not understand audio in " + audio_file_name)
		except sr.RequestError as e:
			result = ' '
			print("Could not request results from Wit.ai service; {0}".format(e))
			print("For file : " + audio_file_name)

		return result
	###

	@staticmethod
	def slice_audio(audio_file_name, slice_duration):
		if(os.path.exists('./trim')):
			shutil.rmtree('./trim')
		
		os.mkdir('trim')

		whole_audio = AudioSegment.from_wav(audio_file_name)
		length = whole_audio.duration_seconds

		num_of_parts = int(length//slice_duration)
		num_of_part_files = num_of_parts

		for i in range(0, num_of_parts):
			part = whole_audio[i*slice_duration*1000:(i+1)*slice_duration*1000]
			part.export('trim/part%d.wav'%(i), format='wav')

		last_part_len = length - num_of_parts*slice_duration
		if(last_part_len >= 5):
			part = whole_audio[-last_part_len*1000:]
			part.export('trim/part%d.wav'%(num_of_parts), format='wav')
			num_of_part_files+=1

		return num_of_part_files
	###

	@staticmethod
	def build_srt(audio_file_name, whole_string, slice_duration):
		srt_file_name = 'TranscribeFromAudio.srt'
		if(os.path.exists(srt_file_name)):
			os.remove(srt_file_name)

		srt_file = open(srt_file_name, 'w')

		for i in range(0, len(whole_string)):
			srt_file.write(str(i+1)+'\n')
			start_time = i*slice_duration
			end_time = (i+1)*slice_duration

			sh = int(start_time//3600)
			sm = int((start_time - sh*3600)//60)
			ss = start_time%60

			eh = int(end_time//3600)
			em = int((end_time - sh*3600)//60)
			es = end_time%60
			
			time_str = '%02d:%02d:%02d,000 --> %02d:%02d:%02d,000\n'%(sh, sm, ss, eh, em, es)
			srt_file.write(time_str)
			srt_file.write(whole_string[i]+'\n\n')

		srt_file.close()

		return srt_file_name
	###

	@staticmethod
	def build_srt_from_audio(audio_file_name, slice_duration):
		num_of_files = Audio.slice_audio(audio_file_name, slice_duration)

		whole_string = []

		#num_of_files = len(glob.glob('trim/*.wav'))

		for i in range(0, num_of_files):
			part_file_name = 'trim/part%d.wav'%(i)
			part_text = Audio.get_text_from_part_audio_BING(part_file_name)
			#part_text = Audio.get_text_from_part_audio_WIT(part_file_name)
			whole_string.append(part_text)
			print "Transcribed %d/%d part files" %(i+1, num_of_files)
		print '\n'

		return Audio.build_srt(audio_file_name, whole_string, slice_duration)
	###

	@staticmethod
	def extract_audio(video_file_name, output_format='wav'):
		#video_file_name = video_file_name.replace(' ', '\ ')
		file_name_without_format = "".join(video_file_name.split('.')[:-1])
		output_file_name = file_name_without_format + '.' + output_format

		if(os.path.isfile(output_file_name)):
			os.remove(output_file_name)

		inputs = {video_file_name : None}
		outputs = {output_file_name : None}
		ff = ffmpy.FFmpeg(inputs=inputs, outputs=outputs)
		#print ff.cmd
		ff.run()

		return output_file_name
	###

	@staticmethod
	def clean_up(audio_file_name):
		if(os.path.exists('./trim')):
			shutil.rmtree('./trim')
		if(os.path.isfile(audio_file_name)):
			os.remove(audio_file_name)
	###

	@staticmethod
	def transcribe_video_file(video_file_name, slice_duration = 15):
		audio_file_name = Audio.extract_audio(video_file_name)
		
		print '\n\nStarted transcribing...'
		transcribed_srt_file_name = Audio.build_srt_from_audio(audio_file_name, slice_duration)
		
		Audio.clean_up(audio_file_name)

		return transcribed_srt_file_name
	###
###


class WordDistance:
	table_generated = False
	max_distance = 2
	substitute_costs = np.ones((128, 128), dtype=np.float64)

	@staticmethod
	def isalphanum(x):
		if(ord(x) >= ord('a') and ord(x) <= ord('z')):
			return True
		if(ord(x) >= ord('0') and ord(x) <= ord('9')):
			return True
		if(ord(x) >= ord('A') and ord(x) <= ord('Z')):
			return True
		return False

	@staticmethod
	def get_group_index(x):
		same_groups = [['V','v','X','x'],
						['y'],
						['A'],
						['Z', 'z'],
						['I', 'i', 'l', '1'],
						['Y'],
						['J', 'j'],
						['t'],
						['T'],
						['K', 'k'],
						['L'],
						['r'],
						['C', 'c'],
						['F', 'f'],
						['E'],
						['N'],
						['M', 'W', 'w'],
						['U', 'u'],
						['H'],
						['b', 'h', 'd'],
						['n'],
						['D', 'o', 'O', '0'],
						['Q'],
						['P'],
						['q'],
						['R', 'p'],
						['S', 'B', 'G', 'a', 'e', 's', '5', '6'],
						['g'],
						['m'],
						['2'],
						['3'],
						['4'],
						['7'],
						['8'],
						['9']]

		for i in range(0, len(same_groups)):
			if(x in same_groups[i]):
				return i
		print 'Did not find index of ' + x
		return -1
	###

	@staticmethod
	def get_distance(a, b):
		if(WordDistance.isalphanum(a) == False or WordDistance.isalphanum(b) == False):
			return WordDistance.max_distance

		idx1 = WordDistance.get_group_index(a)
		idx2 = WordDistance.get_group_index(b)

		if(idx1 == idx2):
			return 0.6*WordDistance.max_distance/35.0
		return abs(idx1-idx2)*WordDistance.max_distance/35.0
	###


	@staticmethod
	def generate_weight_table():
		if(WordDistance.table_generated == True):
			return
		WordDistance.table_generated = True

		for i in range(0, 128):
			for j in range(i, 128):
				if(i == j):
					WordDistance.substitute_costs[i][j] = 0
				else:
					WordDistance.substitute_costs[i][j] = WordDistance.substitute_costs[j][i] = WordDistance.get_distance(chr(i), chr(j))
		
		return
	###

	@staticmethod
	def issameword(word1, word2):
		WordDistance.generate_weight_table()
		dist = lev(word1, word2, substitute_costs=WordDistance.substitute_costs)

		if(dist < 0.3):
			return True
		return False
	###

	@staticmethod
	def iskeyword_in_wordlist(keyword, wordlist):
		for word in wordlist:
			if(WordDistance.issameword(keyword, word) == True):
				return True
		return False

###
