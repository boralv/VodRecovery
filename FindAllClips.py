from datetime import datetime
import requests
from concurrent.futures import ThreadPoolExecutor
import os

vod_id = ""
streamer = ""

default_directory = os.path.expanduser("~\\Documents")

find_option = input("1) Find clips by tracker url" + "\n" + "2) Find clips by entering vod information" + "\n" + "X) Exit Program" + "\n")

if find_option == "1":

    tracker_url = input("Enter tracker url: ")

    if "twitchtracker" in tracker_url:
        vod_id = tracker_url.split("streams/", 1)[1]
    elif "streamscharts" in tracker_url:
        vod_id = tracker_url.split("streams/", 1)[1]
    elif "sullygnome" in tracker_url:
        vod_id = tracker_url.split("stream/", 1)[1]

    if "twitchtracker" in tracker_url:
        streamer = tracker_url.split("com/", 1)[1].split("/")[0]
    elif "sullygnome" in tracker_url:
        streamer = tracker_url.split("channel/", 1)[1].split("/")[0]
    elif "streamscharts" in tracker_url:
        streamer = tracker_url.split("channels/", 1)[1].split("/")[0]
elif find_option == "2":
    vod_id = input("Enter vod id: ")
    streamer = input("Enter streamer name: ")
elif find_option == "x":
    exit()

hours = input("Enter hour value: ")
minutes = input("Enter minute value: ")

duration = (int(hours) * 60) + int(minutes)
reps = ((duration * 60) + 2000) * 2

print("Duration: " + str(duration))
print("Possible Urls: " + str(reps))

def get_url(url):
    return requests.get(url, timeout=100, stream=True)

original_vod_url_list = ["https://clips-media-assets2.twitch.tv/"+vod_id+"-offset-" + str(i) + ".mp4" for i in range(reps) if i % 2 == 0]

valid_counter = 0

with ThreadPoolExecutor(max_workers=100) as pool:
    url_list = []
    max_url_list_length = 50
    current_list = original_vod_url_list

    for i in range(0, len(original_vod_url_list), max_url_list_length):
        batch = current_list[i:i+max_url_list_length]
        response_list = list(pool.map(get_url, batch))
        for x in response_list:
            url_list.append(x)
            if x.status_code == 200:
                print(x.url)
                valid_counter = valid_counter + 1
                print(datetime.now().strftime("%Y/%m/%d %I:%M:%S -  ") + str(valid_counter) + " Clip(s) Found")
        print(datetime.now().strftime("%Y/%m/%d %I:%M:%S - ") + str(len(url_list)) + " of " + str(round(reps/2)))

valid_url_counter = 0

log_file = input("Do you want to log results to file: ")

for response in url_list:
    if response.status_code == 200:
        valid_url_counter = valid_url_counter + 1
        if valid_url_counter > 0:
            print(str(valid_url_counter) + " - " + response.url)
            if log_file.lower() == "y":
                file_name = default_directory+"\\"+streamer+"_"+vod_id + "_log.txt"
                log = open(file_name, "a")
                log.write(response.url + "\n")
            else:
                pass
