from datetime import timedelta
import datetime
import time
import hashlib
from concurrent.futures import ThreadPoolExecutor
import requests
import os

"""
* Created By: ItIckeYd 
* Purpose: The following script retrieves the m3u8 to sub-only and deleted twitch videos.
* Date: May 3rd, 2022
*
* Versions:
*
* 1.0 - Initial Release - May 3rd, 2022
* 1.1 - Renamed variables, refactored code to implement methods, added conditionals.
"""

domains = ["https://vod-secure.twitch.tv/",
"https://vod-metro.twitch.tv/",
"https://vod-pop-secure.twitch.tv/",
"https://d2e2de1etea730.cloudfront.net/",
"https://dqrpb9wgowsf5.cloudfront.net/",
"https://ds0h3roq6wcgc.cloudfront.net/",
"https://d2nvs31859zcd8.cloudfront.net/",
"https://d2aba1wr3818hz.cloudfront.net/",
"https://d3c27h4odz752x.cloudfront.net/",
"https://dgeft87wbj63p.cloudfront.net/",
"https://d1m7jfoe9zdc1j.cloudfront.net/",
"https://d3vd9lfkzbru3h.cloudfront.net/",
"https://d2vjef5jvl6bfs.cloudfront.net/",
"https://d1ymi26ma8va5x.cloudfront.net/",
"https://d1mhjrowxxagfy.cloudfront.net/",
"https://ddacn6pr5v0tl.cloudfront.net/",
"https://d3aqoihi2n8ty8.cloudfront.net/"]

all_possible_urls = []
valid_url_list = []
list_of_lines = []


streamer_name = input("Enter streamer name: ").strip()
vodID = input("Enter vod id: ").strip()
timestamp = input("Enter VOD timestamp (YYYY-MM-DD HH:MM:SS): ").strip()

def get_default_directory():
    default_directory = os.path.expanduser("~\\Documents\\")
    return default_directory

def generate_unmuted_filename():
    unmuted_file_name = get_default_directory()+"VodRecovery_" + vodID + ".m3u8"
    return unmuted_file_name

formatted_date = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")

days_between = datetime.datetime.today() - formatted_date

if days_between > timedelta(days=60):
    print("Vod is " + str(days_between.days) + " days old. Vods typically cannot be recovered when older then 60 days.")
    user_continue = input("Do you want to continue (Y/N): ")
    if user_continue.upper() == "Y":
        pass
    else:
        exit()

def get_url(url):
    return requests.get(url, timeout=100)

for bf_second in range(60):
    vod_date = datetime.datetime(formatted_date.year,formatted_date.month,formatted_date.day,formatted_date.hour,formatted_date.minute,bf_second)
    converted_timestamp = round(time.mktime(vod_date.timetuple()))
    base_url = streamer_name + "_" + vodID + "_" + str(int(converted_timestamp))
    hashed_base_url = str(hashlib.sha1(base_url.encode('utf-8')).hexdigest())[:20]
    formatted_base_url = hashed_base_url + '_' +  base_url
    for domain in domains:
        url = domain+formatted_base_url+"/chunked/index-dvr.m3u8"
        all_possible_urls.append(url)

with ThreadPoolExecutor(max_workers=100) as pool:
    max_url_list_length = 100
    current_list = all_possible_urls

    for i in range(0, len(current_list), max_url_list_length):
        batch = current_list[i:i + max_url_list_length]
        response_list = list(pool.map(get_url, batch))
        for m3u8_url in response_list:
            if m3u8_url.status_code == 200:
                print(m3u8_url.url)
                valid_url_list.append(m3u8_url.url)

def return_valid_links():
    if valid_url_list:
        for link in valid_url_list:
            return link


def bool_is_muted():
    is_muted = False
    vod_response = get_url(valid_url_list[0])
    if "-unmuted" not in vod_response.text:
        is_muted = False
    else:
        is_muted = True
    return is_muted

def unmute_vod():
    link_response = get_url(valid_url_list[0])
    temp_file = open(generate_unmuted_filename(), "w")
    temp_file.write(link_response.text)
    temp_file.close()
    with open(generate_unmuted_filename(), "r") as append_file:
        for line in append_file.readlines():
            list_of_lines.append(line)
            append_file.close()
            counter = 0
            with open(generate_unmuted_filename(), "w") as file:
                for segment in list_of_lines:
                    if "-unmuted" in segment and not segment.startswith("#"):
                        counter = counter + 1
                        url = link_response.url.replace("index-dvr.m3u8", "")
                        file.write(
                            segment.replace(segment, str(url) + str(counter - 1)) + "-muted.ts" + "\n")
                    elif "-unmuted" not in segment and not segment.startswith("#"):
                        counter = counter + 1
                        file.write(segment.replace(segment, str(url) + str(counter - 1)) + ".ts" + "\n")
                    else:
                        file.write(segment)
            file.close()
    print(os.path.basename(generate_unmuted_filename())+" Has been unmuted. File can be found in " + generate_unmuted_filename())

if return_valid_links():
    if bool_is_muted:
        print("Vod contains muted segments")
        bool_unmute_vod = input("Would you like to unmute the vod (Y/N): ")
        if bool_unmute_vod.upper() == "Y":
            unmute_vod()
    else:
        print("Vod does NOT contain muted segments")
else:
    print("No vods found using current domain list.")

input("Press Enter to exit!")