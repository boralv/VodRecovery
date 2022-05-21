import requests
from concurrent.futures import ThreadPoolExecutor
import random

vod_id = input("Enter vod id: ")
hours = 2
minutes = 30

duration = (int(hours) * 60) + int(minutes)
reps = ((duration * 60) + 2000) * 2

print("Vod ID: " + vod_id)
print("Duration: " + str(duration))

def get_url(url):
    return requests.get(url, timeout=100,stream=True)

first_clip_url_type_list = ["https://clips-media-assets2.twitch.tv/" + vod_id + "-offset-" + str(i) + ".mp4" for i in range(reps) if i % 2 == 0]
second_clip_url_type_list = ["https://clips-media-assets2.twitch.tv/"+vod_id+"-index-000000" + str(int(0000000000+i)) + ".mp4" for i in range(reps) if i % 2 == 0]
third_clip_url_type_list = ["https://clips-media-assets2.twitch.tv/vod-" + vod_id + "-offset-" + str(i) + ".mp4" for i in range(reps) if i % 2 == 0]

full_clip_url_list = first_clip_url_type_list + second_clip_url_type_list + third_clip_url_type_list

random.shuffle(full_clip_url_list)

print("Total Number of Urls: " + str(len(full_clip_url_list)))

with ThreadPoolExecutor(max_workers=100) as pool:
    url_list = []
    max_url_list_length = 1000
    current_list = full_clip_url_list

    for i in range(0, len(full_clip_url_list), max_url_list_length):
        batch = current_list[i:i + max_url_list_length]
        response_list = list(pool.map(get_url, batch))
        for index, elem in enumerate(response_list):
            url_list.append(elem)
            if elem.status_code == 200:
                print(elem.url)
                next_url = input("Do you want another url (Y/N): ")
                if next_url.lower() == "y":
                    if response_list[index+1].status_code == 200:
                        print(response_list[index+1].url)
                else:
                    exit()
