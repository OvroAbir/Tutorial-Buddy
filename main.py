from api_collection import *


file=Youtube.download(video_id="1p6LfUkWPKI", download_folder="/home/joy/Desktop")

# print file

keywords=['assembly', 'programming', 'x86', 'denial', 'service']
temp="/home/joy/Desktop/snapshots"

Video.extract_frames(file, folder=temp)
Video.eliminate_irrelevants(folder=temp)

print '\n\nFrom tesseract:'
print Frame.get_matched_snapshots(temp, keywords)

'''print '\n\nAnalysis using subtile:'

srtfile = '1.srt'
subs = pysrt.open(srtfile)

keywords = ['assembly', 'language']
matched_subs = Subtitle.get_matched_subs(subs, keywords)
Subtitle.print_subs(matched_subs)

#f = Audio.transcribe_video_file("/home/joy/Desktop/ffile.mp4")

print 'Here'
print Youtube.download_subtitle('1p6LfUkWPKI')'''