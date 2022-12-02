import os
import glob
import re
import json
import boto3
from collections import defaultdict
from urllib import parse
from functools import partial
from multiprocessing.pool import ThreadPool 

s3 = boto3.client('s3')

VIDEO_FORMAT = "mp4"
EPS = glob.glob(f"./episodes/*.{VIDEO_FORMAT}")
FPS = 1
REGX = re.compile(
  r"(?:.*)(?:S|season)(?:\s|-)*(\d+)(?:\s|x|-|.)*(?:e|x|episode|ep)(?:\s|-)*(\d+)", 
  re.IGNORECASE
)
SHOW_NAME = ""
SHOW_BUCKET_NAME = ""
FRAMES = f"{SHOW_BUCKET_NAME}_frames"
SHOW_DATA = defaultdict(dict)
if not os.path.isdir(FRAMES): os.mkdir(FRAMES)


def main():
  for ep in EPS:
    ep_regx = REGX.match(ep)
    if ep_regx:
      season, episode = list(map(int, ep_regx.groups()))
      dest = f"./{FRAMES}/{season}/{episode}"
      if not os.path.isdir(dest):
        os.makedirs(dest)
        os.system(f'ffmpeg -i "{ep}" -vf "fps={FPS},scale=640:360" {dest}/%d.jpg')
        SHOW_DATA[season][episode] = len(glob.glob(f"{dest}/*.jpg"))
        with open("./lambda/data.json", "w") as json_output:
          json_output.write(json.dumps(dict(SHOW_DATA), sort_keys=True, indent=2))
      else:
        print(f"Season {season} Episode {episode} already process or error occured in last process")

  with open("./lambda/data.json") as data_json:
    SHOW_DATA = json.loads(data_json.read())

  pool = ThreadPool(processes=100) 
  for season in SHOW_DATA:
    for episode in SHOW_DATA[season]:
      episode = str(episode)
      location = f"./{FRAMES}/{season}/{episode}"
      episode_frames = glob.glob(f"{location}/*jpg")
      upload = partial(upload_frame, season, episode)
      pool.map(upload, episode_frames)
      print(f"Season {season.zfill(2)} Episode {episode.zfill(2)} UPLOADED")

def upload_frame(season, episode, frame):
  frame_no = frame[frame.rfind("/") + 1: frame.rfind(".")]
  destination = f"{season}/{episode}/{frame_no}.jpg"
  tag = {
    "name": f"{SHOW_NAME} - Season {season.zfill(2)} Episode {episode.zfill(2)} - Frame {frame_no} of {SHOW_DATA[season][episode]}"
  }
  s3.upload_file(frame, SHOW_BUCKET_NAME, destination, ExtraArgs={"Tagging": parse.urlencode(tag)})


if __name__ == "__main__":
  raise SystemExit(main())