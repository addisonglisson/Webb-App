import os
from googleapiclient.discovery import build

YOUTUBE_API_KEY = "AIzaSyBtW0DbuuqFMLz31MJyCy5lwRC8Zm60o8E"


youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY, credentials=None)

def get_video_id(url):
    if "watch?v=" in url:
        return url.split("watch?v=")[1][:11]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1][:11]
    return None

def get_captions(video_id):
    try:
        results = youtube.captions().list(part="snippet", videoId=video_id).execute()
        captions = []
        for item in results["items"]:
            caption_id = item["id"]
            language = item["snippet"]["language"]
            track_name = item["snippet"]["name"]
            is_default = item["snippet"]["is_default"]
            caption = {
                "id": caption_id,
                "language": language,
                "track_name": track_name,
                "is_default": is_default
            }
            captions.append(caption)
        return captions
    except Exception as e:
        print(f"Error fetching captions: {e}")
        return []
