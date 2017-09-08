from api_collection import *
import os, csv, shutil

def read_input(folder='input'):
	numoffiles = len([f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))])

	input_list = []
	for i in range(numoffiles):
		filename = os.path.join(folder, str(i)+'.csv')
		file = open(filename)
		inp = list(csv.reader(file))
		input_list.append(inp)
		file.close()

	return input_list
###

def clean_up(folder='output'):
	if os.path.exists(folder):
		shutil.rmtree(folder)
###

def get_keywords(keywords_ara):
	keys = []
	for keyword in keywords_ara:
		ks = keyword.split(' ')
		for k in ks:
			if k.isalpha() == True and len(k)>0:
				keys.append(k)
	return keys
###

def driver_function(input):
	clean_up()
	output_folder = 'output'
	os.mkdir(output_folder)

	for filenum in range(len(input)):
		cur_folder = output_folder+'/'+str(filenum+1)
		os.mkdir(cur_folder)

		for video in input[filenum]:
			videoid = video[0]
			video_keywords = get_keywords(video[1:])
			print('Keywords are :')
			print(video_keywords)
			process_video(videoid, video_keywords, cur_folder)
###

def process_video(videoid, keywords, folder):
	videoname = Youtube.getname(videoid)
	videofolder = folder+'/'+Youtube.getname(videoid)
	os.mkdir(videofolder)

	videofilename = Youtube.download(videoid, videofolder)
	
	snapfolder = Video.extract_frames(videofilename, videofolder)
	subfolder = Frame.resize_images_half(snapfolder)
	Video.eliminate_irrelevants(subfolder)
	Frame.delete_high_res_imgs(snapfolder, subfolder)
	shutil.rmtree(subfolder)

	print("Downloading subtitile")
	subfilename = Youtube.download_subtitle(videoid, videofolder)
	if subfilename is None:
		subfilename = Audio.transcribe_video_file(videofilename, videofolder, 25)

	make_decisions(videofilename, keywords, subfilename, snapfolder, videofolder)
###

def make_decisions(videofilename, keywords, subfilename, snapfolder, videofolder):
	duration=Video.get_duration(videofilename)
	#video_points=Frame.get_match_points(snapfolder,keywords)
	print('Getting video intervals...')
	video_intgervals = Frame.get_matched_intervals(snapfolder, keywords)
	print('video intervals : ')
	print(video_intgervals)
	subs = pysrt.open(subfilename)
	#audio_points=Subtitle.get_match_points(subs,keywords)
	print('getting audio intervals...')
	audio_intervals = Subtitle.get_matched_intervals(subs, keywords)
	print('Audio intervals : ')
	print(audio_intervals)
	#hotspots = get_hotspot(duration, audio_points, video_points)
	
	print('Mergeing intervals...')
	intervals = audio_intervals[:]
	for vi in video_intgervals:
		intervals.append(vi)

	minintervaldiff = max(30, duration/20)
	intervals = merge_intervals(intervals, minintervaldiff)
	#times = process_hotspots(hotspots)
	times = process_hotspots(intervals)
	print("Times are : ")
	print(times)
	writeOutputfile(videofolder, times, video_intgervals, audio_intervals)
###

def convert_time(sec):
	Hour = sec//3600
	secInmin = sec - Hour*3600
	Min = secInmin//60
	Sec = secInmin - Min*60
	return (Hour, Min, Sec)
###

def process_hotspots(hotspots):
	times = []
	for i in range(len(hotspots)):
		startSec = hotspots[i][0]
		endSec = hotspots[i][1]
		time = []
		time.append(convert_time(startSec))
		time.append(convert_time(endSec))
		#time.append(hotspots[i][2])
		times.append(time) 
	return times
###

def get_timefrom_tuple(tuple):
	s = str(tuple[0]) + ' hour ' + str(tuple[1]) + ' min ' + str(tuple[2]) + ' sec\n'
	return s
###

def get_string_from_list(lst):
	s = '['
	for l in lst:
		s += '['
		s += str(l[0])
		s += ', '
		s += str(l[1])
		s += '], '
	s += ']\n'
	return s

def writeOutputfile(videofolder, times, vpoints, apoints):
	filename = videofolder + '/' + 'result.txt'
	file = open(filename, 'w')
	string = 'Intervals :\n'
	for i in range(len(times)):
		string += 'Start time : '
		string += get_timefrom_tuple(times[i][0])
		string += 'Ending time : '
		string += get_timefrom_tuple(times[i][1])
		#string += 'Weight : '
		#string += str(times[i][2])
		string += '\n'
	file.write(string)
	
	file.write('Video Intervals : ')
	file.write(get_string_from_list(vpoints))
	
	file.write('\nAudio Intervals : ')
	file.write(get_string_from_list(apoints))

	file.close()
###


input = read_input()
driver_function(input)
print('Finished')