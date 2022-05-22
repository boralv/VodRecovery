import requests
import os
from datetime import datetime
import uuid


print("*********************************")
print("WELCOME TO TWITCH CLIP DOWNLOADER")
print("*********************************")
print()


default_directory = os.path.expanduser("~\\Documents")

tracker_url = input("Enter tracker url: ")

vod_id = ""
streamer_name = ""

if "twitchtracker" in tracker_url:
    vod_id = tracker_url.split("streams/", 1)[1]
elif "streamscharts" in tracker_url:
    vod_id = tracker_url.split("streams/", 1)[1]
elif "sullygnome" in tracker_url:
    vod_id = tracker_url.split("stream/", 1)[1]

if "twitchtracker" in tracker_url:
    streamer_name = tracker_url.split("com/", 1)[1].split("/")[0]
elif "sullygnome" in tracker_url:
    streamer_name = tracker_url.split("channel/", 1)[1].split("/")[0]
elif "streamscharts" in tracker_url:
    streamer_name = tracker_url.split("channels/", 1)[1].split("/")[0]

skipped_lines = int(input("Enter lines to be skipped in file: "))


def get_file_directory():
    file_path = os.path.join(default_directory+"\\"+streamer_name+"_"+vod_id + "_log.txt")
    return file_path


def return_file_contents():
    with open(get_file_directory()) as f:
        content = f.readlines()
        content = [x.strip() for x in content[skipped_lines:]]
    return content


def return_uuid():
    generated_uuid = uuid.uuid4().hex[:8]
    return generated_uuid


def download_clips():
    counter = 0
    print("Starting Download....")
    download_directory = default_directory+"\\"+streamer_name.title()+"_"+vod_id
    if os.path.exists(download_directory):
        pass
    else:
        os.mkdir(download_directory)
    for links in return_file_contents():
        counter = counter + 1
        vod_counter = return_uuid()
        link_url = os.path.basename(links)
        r = requests.get(links, stream=True)
        if r.status_code == 200:
            if "offset" in link_url:
                with open(download_directory+"\\"+streamer_name.title()+"_" + str(vod_id) + "_" + str(vod_counter) + ".mp4", 'wb') as x:
                    print(datetime.now().strftime("%Y/%m/%d %I:%M:%S    ") + "Downloading... Clip " + str(
                        counter) + " of " + str(len(return_file_contents())) + " - " + links + "\n")
                    x.write(r.content)
            elif "AT-cm%" in link_url:
                with open(download_directory+"\\"+streamer_name.title()+"_" + str(vod_id) + "_" + str(vod_counter) + ".mp4", 'wb') as x:
                    print(datetime.now().strftime("%Y/%m/%d %I:%M:%S    ") + "Downloading... Clip " + str(
                        counter) + " of " + str(len(return_file_contents())) + " - " + links)
                    x.write(r.content)
            elif "index-" in link_url:
                with open(download_directory+"\\"+streamer_name.title()+"_" + str(vod_id) + "_" + str(vod_counter) + ".mp4", 'wb') as x:
                    print(datetime.now().strftime("%Y/%m/%d %I:%M:%S    ") + "Downloading... Clip " + str(
                        counter) + " of " + str(len(return_file_contents())) + " - " + links)
                    x.write(r.content)
            else:
                print("ERROR: Please check the log file and failing link!", links)
        else:
            print("ERROR: " + str(r.status_code) + " - " + str(r.reason))
            pass


download_clips()
