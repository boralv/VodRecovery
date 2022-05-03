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

possible_urls = []
valid_m3u8_list = []

default_directory  = os.path.expanduser("~\\Documents\\")

streamer_name = input("Enter streamer name: ").strip()
vodID = input("Enter vod id: ").strip()
timestamp = input("Enter VOD timestamp (YYYY-MM-DD HH:MM:SS): ").strip()

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
        possible_urls.append(url)

with ThreadPoolExecutor(max_workers=100) as pool:
    max_url_list_length = 100
    current_list = possible_urls

    for i in range(0, len(possible_urls), max_url_list_length):
        batch = current_list[i:i + max_url_list_length]
        response_list = list(pool.map(get_url, batch))
        for m3u8_link in response_list:
            if m3u8_link.status_code == 200:
                valid_m3u8_list.append(m3u8_link.url)

for links in valid_m3u8_list:
    print(links)

if not valid_m3u8_list:
    print("No vods found using current domain list")
    input("Press Enter to exit")
    exit()

unmuted_file_name = default_directory+"VodRecovery_" + vodID + ".m3u8"

list_of_lines = []

first_valid_m3u8 = valid_m3u8_list[0]

check_muted = input("Check to see if vod contains muted segments (Y/N): ")
if check_muted.upper() == "Y":
    m3u8_response = requests.get(first_valid_m3u8)
    if "-unmuted" not in m3u8_response.text:
        print("Vod does NOT contain muted segments")
    else:
        print("Vod contains muted segments")
        unmute_vod = input("Would you like to unmute the vod (Y/N): ")
        if unmute_vod.upper() == "Y":
            temp_file = open(unmuted_file_name,"w")
            temp_file.write(m3u8_response.text)
            temp_file.close()
            with open(unmuted_file_name,"r") as append_file:
                for line in append_file.readlines():
                    list_of_lines.append(line)
                    append_file.close()
                    counter = 0
                    with open(unmuted_file_name,"w") as file:
                        for segment in list_of_lines:
                            if "-unmuted" in segment and not segment.startswith("#"):
                                counter = counter + 1
                                first_valid_m3u8 = first_valid_m3u8.replace("index-dvr.m3u8", "")
                                file.write(segment.replace(segment, str(first_valid_m3u8)+str(counter-1))+"-muted.ts" + "\n")
                            elif "-unmuted" not in segment and not segment.startswith("#"):
                                counter = counter + 1
                                file.write(segment.replace(segment, str(first_valid_m3u8) + str(counter-1)) + ".ts" + "\n")
                            else:
                                 file.write(segment)
                    file.close()

input("Press Enter to exit!")