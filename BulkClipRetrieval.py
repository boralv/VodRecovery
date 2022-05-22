import requests
from concurrent.futures import ThreadPoolExecutor
import os

streamer = input("Enter Streamer:")

file_path = input("Enter full path of sullygnome CSV file: ")

source_file = open(file_path, "r+")

default_directory = os.path.expanduser("~\\Documents")

lines = source_file.readlines()[1:]

vod_info = {}

for line in lines:
    if line.strip():
        filtered_line = line.partition("stream/")[2]
        final_string = filtered_line.split(",")
        reps = ((int(final_string[1].strip()) * 60) + 2000) * 2
        vod_info.update({final_string[0]:reps})

counter = 0

valid_counter = 0

def get_url(url):
    return requests.get(url, timeout=100, stream=True)

def get_head(url):
    return requests.head(url, timeout=100, stream=True)

for vod, duration in vod_info.items():
    counter += 1
    print("Processing Twitch Vod... " + str(vod) + " - " + str(counter) + " of " + str(len(vod_info)))

    original_vod_url_list = ["https://clips-media-assets2.twitch.tv/" + str(vod) + "-offset-" + str(i) + ".mp4" for i in
                             range(duration) if i % 2 == 0]

    with ThreadPoolExecutor(max_workers=100) as pool:
        url_list = []
        max_url_list_length = 250
        current_list = original_vod_url_list

        for i in range(0, len(original_vod_url_list), max_url_list_length):
            batch = current_list[i:i + max_url_list_length]
            response_list = list(pool.map(get_head, batch))
            for index, elem in enumerate(response_list):
                url_list.append(elem)
                if elem.status_code == 200:
                    valid_counter +=1
                    print(elem.url)
                    if valid_counter >= 1:
                        file_name = default_directory + "\\" + streamer + "_" + vod + "_log.txt"
                        log = open(file_name, "a+")
                        log.write(elem.url + "\n")
                    print(str(valid_counter) + " Clip(s) Found")
                else:
                    pass
            print(str(len(url_list)) + " of " + str(round(duration / 2)))
    valid_counter = 0
