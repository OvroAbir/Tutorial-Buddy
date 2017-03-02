class YoutubeSearch:
	@staticmethod
	def search(search_term, max_results=25):
		from apiclient.discovery import build
		from apiclient.errors import HttpError
		from oauth2client.tools import argparser

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
			print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
	###
###