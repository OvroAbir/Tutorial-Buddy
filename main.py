from api_collection import *
from os.path import expanduser as native_path

f=Youtube.download(video_id="1p6LfUkWPKI", download_folder=native_path("~/Desktop"))

keywords=['assembly']
temp=native_path("~/Desktop/snapshots")

# Video.extract_frames(f, folder=temp)
# Video.eliminate_irrelevants(folder=temp)

duration=Video.get_duration(f)

video_points=Frame.get_match_points(temp,keywords)
# Youtube.download_subtitle('1p6LfUkWPKI')

print video_points

srtfile = '1p6LfUkWPKI.en.srt'
subs = pysrt.open(srtfile)

audio_points=Subtitle.get_match_points(subs,keywords)

print get_hotspot(duration, audio_points, video_points)

# Audio.transcribe_video_file(f)
