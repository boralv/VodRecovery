import time
from datetime import timedelta
import datetime
import pytz
import hashlib
from concurrent.futures import ThreadPoolExecutor
import requests
import os
import random

"""
* Created By: ItIckeYd 
* Purpose: The following script retrieves the m3u8 to sub-only and deleted twitch videos.
* Date: May 3rd, 2022
*
* Versions:
*
* 1.0 - Initial Release - May 3rd, 2022
* 1.1 - Renamed variables, refactored code to implement methods, added conditionals.
* 1.2 - Refactored date check and added a main.
* 1.3 - Refactored code to retrieve the formatted date.
* 1.4 - Refactored retrieving valid links and main.
* 1.5 - Fixed unmuting speed.
* 1.6 - Fixed bug where script was only returning "Vod contains muted segments"
* 1.7 - Added functionality to check 100 random segments status codes.
* 1.8 - Added output for the user when segments are not available.
* 1.9 - Added functionality to check segment availability if the vod does not contain muted segments
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
segment_list = []

print("**Welcome To Vod Recovery**")

streamer_name = input("Enter streamer name: ").strip()
vodID = input("Enter vod id: ").strip()
timestamp = input("Enter VOD timestamp (YYYY-MM-DD HH:MM:SS): ").strip()

def get_url(url):
    return requests.get(url,stream=True)

def format_timestamp(vod_datetime):
    formatted_date = datetime.datetime.strptime(vod_datetime, "%Y-%m-%d %H:%M:%S")
    return formatted_date

def get_default_directory():
    default_directory = os.path.expanduser("~\\Documents\\")
    return default_directory

def generate_vod_filename():
    unmuted_file_name = get_default_directory()+"VodRecovery_" + vodID + ".m3u8"
    return unmuted_file_name

def get_vod_age():
    return datetime.datetime.today() - format_timestamp(timestamp)

def is_vod_date_greater_60():
    if get_vod_age() > timedelta(days=60):
        bool_vod_expired = True
    else:
        bool_vod_expired = False
    return bool_vod_expired

def remove_file(file_path):
    if os.path.exists(file_path):
        return os.remove(file_path)

def get_valid_links():
    for bf_second in range(60):
        vod_date = datetime.datetime(format_timestamp(timestamp).year,format_timestamp(timestamp).month,format_timestamp(timestamp).day,format_timestamp(timestamp).hour,format_timestamp(timestamp).minute,bf_second)
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
                    valid_url_list.append(m3u8_url.url)
        for valid_url in valid_url_list:
            print(valid_url)
    return valid_url_list

def bool_is_muted():
    vod_response = get_url(valid_url_list[0])
    if "unmuted" in vod_response.text:
       is_muted = True
    else:
        is_muted = False
    return is_muted

def unmute_vod():
    link_response = get_url(valid_url_list[0])
    temp_file = open(generate_vod_filename(), "w")
    temp_file.write(link_response.text)
    temp_file.close()
    with open(generate_vod_filename(), "r") as append_file:
        for line in append_file.readlines():
            list_of_lines.append(line)
    append_file.close()
    counter = 0
    with open(generate_vod_filename(), "w") as file:
        for segment in list_of_lines:
            url = link_response.url.replace("index-dvr.m3u8", "")
            if "-unmuted" in segment and not segment.startswith("#"):
                counter += 1
                file.write(
                    segment.replace(segment, str(url) + str(counter - 1)) + "-muted.ts" + "\n")
                segment_list.append(str(url) + str(counter - 1) + "-muted.ts")
            elif "-unmuted" not in segment and not segment.startswith("#"):
                counter += 1
                file.write(segment.replace(segment, str(url) + str(counter - 1)) + ".ts" + "\n")
                segment_list.append(str(url) + str(counter - 1) + ".ts")
            else:
                 file.write(segment)
    file.close()
    print(os.path.basename(generate_vod_filename())+" Has been unmuted. File can be found in " + generate_vod_filename())

def create_temp_vod_file():
    link_response = get_url(valid_url_list[0])
    temp_file = open(generate_vod_filename(), "w")
    temp_file.write(link_response.text)
    temp_file.close()
    with open(generate_vod_filename(), "r") as append_file:
        for line in append_file.readlines():
            list_of_lines.append(line)
    append_file.close()
    counter = 0
    with open(generate_vod_filename(), "w") as file:
        for segment in list_of_lines:
            url = link_response.url.replace("index-dvr.m3u8", "")
            if "-unmuted" not in segment and not segment.startswith("#"):
                counter += 1
                file.write(segment.replace(segment, str(url) + str(counter - 1)) + ".ts" + "\n")
                segment_list.append(str(url) + str(counter - 1) + ".ts")
            else:
                file.write(segment)
    file.close()

def get_number_of_segments(list):
    return len(list)

def check_segment_availability():
    valid_segment_counter = 0
    random.shuffle(segment_list)
    with ThreadPoolExecutor(max_workers=50) as pool:
        max_url_list_length = 25
        current_list = segment_list[0:100]
        for i in range(0, len(current_list), max_url_list_length):
            batch = current_list[i:i + max_url_list_length]
            response_list = list(pool.map(get_url, batch))
            for segment_response in response_list:
                if segment_response.status_code == 200:
                    valid_segment_counter +=1
    return valid_segment_counter

def recover_vod():
    if get_valid_links():
        if bool_is_muted():
            print("Vod contains muted segments")
            bool_unmute_vod = input("Would you like to unmute the vod (Y/N): ")
            if bool_unmute_vod.upper() == "Y":
                unmute_vod()
                print("Total Number of Segments: " + str(get_number_of_segments(segment_list)))
                check_segment = input("Would you like to check if segments are valid (Y/N): ")
                valid_segments = check_segment_availability()
                if check_segment.upper() == "Y":
                    if valid_segments < 100:
                        print("Out of the 100 random segments checked " + str(valid_segments) + " are valid. Due to segments not being available the vod may not be playable at certain places or at all.")
                    else:
                        print("All segments that were checked are valid.")
                else:
                    pass
        else:
            print("Vod does NOT contain muted segments")
            check_segment = input("Would you like to check if segments are valid (Y/N): ")
            if check_segment.upper() == "Y":
                create_temp_vod_file()
                valid_segments = check_segment_availability()
                if valid_segments < 100:
                    print("Out of the 100 random segments checked " + str(
                        valid_segments) + " are valid. Due to segments not being available the vod may not be playable at certain places or at all.")
                    remove_file(generate_vod_filename())
                else:
                    print("All segments that were checked are valid.")
                    remove_file(generate_vod_filename())
            else:
                pass

    else:
        print("No vods found using current domain list.")


if not is_vod_date_greater_60():
    recover_vod()
else:
    print("Vod is " + str(get_vod_age().days) + " days old. Vods typically cannot be recovered when older then 60 days.")
    user_continue = input("Do you want to continue (Y/N): ")
    if user_continue.upper() == "Y":
        recover_vod()
    else:
        exit()