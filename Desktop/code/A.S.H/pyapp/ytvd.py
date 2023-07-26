from googleapiclient.discovery import build
import json

# Enter your API key
API_KEY = "AIzaSyBgGAo9nkSzMyP9I4laDCGieNQ_yYt7peg"

# Create a YouTube Data API service instance
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Get the most recent 25 videos from your YouTube watch history
watch_history_request = youtube.activities().list(
    part='snippet,contentDetails',
    mine=True,
    maxResults=2,
    fields='items(snippet(title,tags)),nextPageToken'
)
watch_history_response = watch_history_request.execute()

# Process the response and extract the tags from each video
tags = []
for item in watch_history_response['items']:
    video_title = item['snippet']['title']
    video_tags = item['snippet'].get('tags', [])
    tags.extend(video_tags)

# Count the occurrences of each tag
tag_counts = {}
for tag in tags:
    if tag in tag_counts:
        tag_counts[tag] += 1
    else:
        tag_counts[tag] = 1

# Find the most watched tag
most_watched_tag = max(tag_counts, key=tag_counts.get)

# Print the most watched tag
print("Most watched tag:", most_watched_tag)
