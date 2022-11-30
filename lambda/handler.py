import os
import io
import boto3
import tweepy
import zipfile
import uuid
import json

lambda_client = boto3.client('lambda')

CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = os.environ['ACCESS_TOKEN_SECRET']
BUCKET_NAME = os.environ['BUCKET_NAME']
SHOW = os.environ['SHOW']
TWEETS_PER_ITERATION = 5
CLOUD_WATCH_EVENT_RULE = "every_frame_bot"
with open("data.json") as json_data:
  SHOW_DATA = json.load(json_data)

class TweetS3Images:
  def __init__(self, api, client, bucket):
    self._api = api
    self._client = client
    self._bucket = bucket

  def tweet(self, bucket, file_name):
    temp_file = f"/tmp/{uuid.uuid4()}"
    self._client.download_file(bucket, file_name, temp_file)
    tweet_text = self.get_tweet_text(bucket, file_name)
    self._api.update_status_with_media(tweet_text, temp_file)

    try:
      os.remove(temp_file)
    except OSError as e:
      raise(e)

  def get_tweet_text(self, bucket, file_name):
    tags = self._client.get_object_tagging(Bucket=bucket, Key=file_name)

    if "TagSet" in tags and tags["TagSet"]:
      return tags["TagSet"][0]["Value"]
    else:
      season, episode, frame = file_name.split("/")
      frame = frame[:frame.rfind(".")]
      return f"{SHOW} - Season {season.zfill(2)} Episode {episode.zfill(2)} - Frame {frame} of {SHOW_DATA[season][episode]}"


def lambda_handler(event: object, context: object):
  try:
    auth = tweepy.OAuth1UserHandler(
      CONSUMER_KEY, 
      CONSUMER_SECRET, 
      ACCESS_TOKEN, 
      ACCESS_TOKEN_SECRET
    )
    api = tweepy.API(auth)
    client = boto3.client('s3')

    try:
      with open('state.txt') as f:
        season, episode, frame = list(map(int, f.read().strip().split(',')))
    except FileNotFoundError:
        season, episode, frame = 1, 1, 1


    TWEETER = TweetS3Images(api, client, BUCKET_NAME)

    for i in range(TWEETS_PER_ITERATION):
      if frame > SHOW_DATA[str(season)][str(episode)]:
        frame, episode = 1, episode + 1
      
      if str(episode) not in SHOW_DATA[str(season)]:
        season, episode = season + 1, 1

      if str(season) not in SHOW_DATA:
        print(season)
        # Show finished, Disable Cloudwatch event triggers 
        cloud_watch_client = boto3.client('events')
        response = cloud_watch_client.remove_targets(
          Rule = CLOUD_WATCH_EVENT_RULE,
          Ids=["every_frame_bot"]
        )
        return

      frame_file_path = f"{season}/{episode}/{frame}.jpg"
      TWEETER.tweet(BUCKET_NAME, frame_file_path)

      frame += 1

    # Update State File

    bio = io.BytesIO()
    with zipfile.ZipFile(bio, 'w') as zipf:
      for root, dirs, files in os.walk("."):
        for file in files:
          if file != 'state.txt':
            zipf.write(
              os.path.join(root, file), 
            )
          else:
            info = zipfile.ZipInfo(os.path.join(root, file))
            info.external_attr = 0o644 << 16
            zipf.writestr(info, f'{season},{episode},{frame}')

    lambda_client.update_function_code(
      FunctionName=context.function_name,
      ZipFile=bio.getvalue(),
    )
  except Exception as e:
    print(e)
    raise e

def main() -> int:
  lambda_handler(None, None)
  return 0

if __name__ == '__main__':
  raise SystemExit(main())