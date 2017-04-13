from api_collection import *
import glob


def get_matched_snapshots(folder, keywords):
	matched_img_names = []
	img_names = glob.glob(folder + '/*.jpeg')
	for img_name in img_names:
		words = Frame.extract_words(img_name)
		for word in words:
			if(word in keywords and img_name not in matched_img_names):
				matched_img_names.append(img_name)
	return matched_img_names
###

'''
file=Youtube.download(video_id="1p6LfUkWPKI", download_folder="/home/joy/Desktop")

# print file

keywords=['assembly', 'programming', 'x86', 'denial', 'service']
temp="/home/joy/Desktop/snapshots"

Video.extract_frames(file, folder=temp)
Video.eliminate_irrelevants(folder=temp)

print '\n\nFrom tesseract:'
print get_matched_snapshots(temp, keywords)

print '\n\nAnalysis using subtile:'

srtfile = '1.srt'
subs = pysrt.open(srtfile)

keywords = ['assembly', 'language']
matched_subs = Subtitle.get_matched_subs(subs, keywords)
Subtitle.print_subs(matched_subs)
'''
f = Audio.transcribe_video_file("/home/joy/Desktop/ffile.mp4")