import datetime
import hashlib
import os
import random
from datetime import timedelta
import grequests
import requests
import json

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

def return_main_menu():
    menu = "\n" + "1) Recover Live" + "\n" + "2) Recover VOD" + "\n" + "3) Recover Clips" + "\n" + "4) Download/Unmute an M3U8 file" + "\n" + "5) Check M3U8 Segments" + "\n" + "6) Exit" + "\n"
    print(menu)

def get_default_directory():
    return os.path.expanduser("~\\Documents\\")

def generate_log_filename(directory, streamer, vod_id):
    file_path = os.path.join(directory + "\\" + streamer + "_" + vod_id + "_log.txt")
    return file_path

def generate_vod_filename(streamer, vod_id):
    vod_filename = get_default_directory() + "VodRecovery_" + streamer + "_" + vod_id + ".m3u8"
    return vod_filename


def generate_website_links(streamer, vod_id):
    website_list = ["https://sullygnome.com/channel/" + streamer + "/stream/" + vod_id,
                    "https://twitchtracker.com/" + streamer + "/streams/" + vod_id,
                    "https://streamscharts.com/channels/" + streamer + "/streams/" + vod_id]
    return website_list

def remove_file(file_path):
    if os.path.exists(file_path):
        return os.remove(file_path)

def format_timestamp(timestamp):
    # Process RFC 3339 format
    timestamp = timestamp.replace('T', ' ')
    timestamp = timestamp.replace('Z', '')
    if timestamp.count(":") == 1:
        timestamp = timestamp + ":00"
    formatted_date = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    return formatted_date

def get_vod_age(timestamp):
    vod_age = datetime.datetime.today() - format_timestamp(timestamp)
    return 0 if vod_age.days <= 0 else vod_age.days

def vod_is_muted(url):
    return bool("unmuted" in requests.get(url).text)

def get_duration(hours, minutes):
    return (int(hours) * 60) + int(minutes)

def get_reps(duration):
    reps = ((duration * 60) + 2000) * 2
    return reps

def get_all_clip_urls(vod_id, reps):
    first_clip_list = ["https://clips-media-assets2.twitch.tv/" + vod_id + "-offset-" + str(i) + ".mp4" for i in
                       range(reps) if i % 2 == 0]

    second_clip_list = [
        "https://clips-media-assets2.twitch.tv/" + vod_id + "-index-" + "%010g" % (int('000000000') + i) + ".mp4" for i
        in range(reps) if i % 2 == 0]

    third_clip_list = ["https://clips-media-assets2.twitch.tv/vod-" + vod_id + "-offset-" + str(i) + ".mp4" for i in
                       range(reps) if i % 2 == 0]

    clip_format = input(
        "What clip url format would you like to use (format is NOT guaranteed for the time periods suggested)? " + "\n" + "1) Default - Most vods use this format" + "\n" + "2) Archived - common between 2016-2017" + "\n" + "3) Alternate - common between 2017-2019" + "\n")

    if clip_format == "1":
        return first_clip_list
    elif clip_format == "2":
        return second_clip_list
    elif clip_format == "3":
        return third_clip_list
    else:
        print("Invalid option! Returning to main menu.")
        return

def parse_m3u8_link(url):
    streamer = url.split("_")[1]
    vod_id = url.split("_")[2].split("/")[0]
    return streamer, vod_id

def return_file_contents(directory, streamer, vod_id):
    with open(generate_log_filename(directory, streamer, vod_id)) as f:
        content = f.readlines()
        content = [x.strip() for x in content]
    return content

def get_all_urls(streamer, vod_id, timestamp):
    vod_url_list = []
    for seconds in range(60):
        epoch_timestamp = ((format_timestamp(timestamp) + timedelta(seconds=seconds)) - datetime.datetime(1970, 1, 1)).total_seconds()
        base_url = streamer + "_" + vod_id + "_" + str(int(epoch_timestamp))
        hashed_base_url = str(hashlib.sha1(base_url.encode('utf-8')).hexdigest())[:20]
        for domain in domains:
            vod_url_list.append(domain + hashed_base_url + "_" + base_url + "/chunked/index-dvr.m3u8")
    return vod_url_list

def get_valid_urls(url_list):
    valid_url_list = []
    rs = (grequests.head(u) for u in url_list)
    for result in grequests.imap(rs, size=100):
        if result.status_code == 200:
            valid_url_list.append(result.url)
            break
    return valid_url_list

def unmute_vod(url):
    file_contents = []
    counter = 0
    vod_file_path = generate_vod_filename(parse_m3u8_link(url)[0], parse_m3u8_link(url)[1])
    with open(vod_file_path, "w") as vod_file:
        vod_file.write(requests.get(url, stream=True).text)
    vod_file.close()
    with open(vod_file_path, "r") as vod_file:
        for lines in vod_file.readlines():
            file_contents.append(lines)
    vod_file.close()
    with open(vod_file_path, "w") as vod_file:
        for segment in file_contents:
            url = url.replace("index-dvr.m3u8", "")
            if "-unmuted" in segment and not segment.startswith("#"):
                counter += 1
                vod_file.write(segment.replace(segment, str(url) + str(counter - 1)) + "-muted.ts" + "\n")
            elif "-unmuted" not in segment and not segment.startswith("#"):
                counter += 1
                vod_file.write(segment.replace(segment, str(url) + str(counter - 1)) + ".ts" + "\n")
            else:
                vod_file.write(segment)
    vod_file.close()
    print(os.path.basename(vod_file_path) + " Has been unmuted. File can be found in " + vod_file_path)

def get_segments(url):
    counter = 0
    file_contents, segment_list = [], []
    vod_file_path = generate_vod_filename(parse_m3u8_link(url)[0], parse_m3u8_link(url)[1])
    if os.path.exists(vod_file_path):
        with open(vod_file_path, "r+") as vod_file:
            for segment in vod_file.readlines():
                url = url.replace("index-dvr.m3u8", "")
                if "-muted" in segment and not segment.startswith("#"):
                    counter += 1
                    segment_list.append(str(url) + str(counter - 1) + "-muted.ts")
                elif "-muted" not in segment and not segment.startswith("#"):
                    counter += 1
                    segment_list.append(str(url) + str(counter - 1) + ".ts")
                else:
                    pass
        vod_file.close()
    else:
        with open(vod_file_path, "w") as vod_file:
            vod_file.write(requests.get(url, stream=True).text)
        vod_file.close()
        with open(vod_file_path, "r") as vod_file:
            for lines in vod_file.readlines():
                file_contents.append(lines)
        vod_file.close()
        counter = 0
        with open(vod_file_path, "w") as unmuted_vod_file:
            for segment in file_contents:
                url = url.replace("index-dvr.m3u8", "")
                if "-unmuted" in segment and not segment.startswith("#"):
                    counter += 1
                    unmuted_vod_file.write(segment.replace(segment, str(url) + str(counter - 1)) + "-muted.ts" + "\n")
                    segment_list.append(str(url) + str(counter - 1) + "-muted.ts")
                elif "-unmuted" not in segment and not segment.startswith("#"):
                    counter += 1
                    unmuted_vod_file.write(segment.replace(segment, str(url) + str(counter - 1)) + ".ts" + "\n")
                    segment_list.append(str(url) + str(counter - 1) + ".ts")
                else:
                    pass
        unmuted_vod_file.close()
    return segment_list

def check_segment_availability(segments):
    valid_segment_counter = 0
    all_segments = []
    for url in segments:
        all_segments.append(url.strip())
    rs = (grequests.head(u) for u in all_segments)
    for result in grequests.imap(rs, size=100):
        if result.status_code == 200:
            valid_segment_counter += 1
    return valid_segment_counter

def check_segments(url):
    segments = get_segments(url)
    print(str(check_segment_availability(segments)) + " of " + str(len(segments)) + " segments are valid.")
    remove_file(generate_vod_filename(parse_m3u8_link(url)[0], parse_m3u8_link(url)[1]))

def get_streamer_name():
    streamer_name = input("Enter streamer name: ")
    return streamer_name

def recover_live():
    file_path = "twitch-auth.json"
    with open(file_path, "a") as auth_file:
        if os.stat(file_path).st_size == 0:
            user_option = input("Do you want to authenticate with Twitch? (Y/N): ")
            if user_option.upper() == "Y":
                client_id = input("Client ID: ")
                token = input("Access Token: ")
                auth = {
                    "Client-Id": client_id,
                    "Authorization": "Bearer {token}"
                }
                json_object = json.dumps(auth, indent=4)
                auth_file.write(json_object)
            else:
                return
    url = "https://api.twitch.tv/helix/streams"
    streamer_name = get_streamer_name()
    params = {
        'user_login': streamer_name,
    }
    with open(file_path, "r") as auth_file:
        headers = json.load(auth_file)
    r = requests.get(url=url, params=params, headers=headers)
    if r.status_code == 200:
        dict = r.json()
        if len(dict["data"]) > 0:
            vodID = dict["data"][0]["id"] 
            timestamp = dict["data"][0]["started_at"]
            recover_vod(streamer_name, vodID, timestamp)
        else:
            user_option = input(f"{streamer_name} is not live! Do you want to recover past VOD? (Y/N): ")
            if user_option.upper() == "Y":
                recover_vod_manual(streamer_name)
    else:
        print("ERROR: " + str(r.status_code) + " - " + str(r.reason))
        pass

def recover_vod_manual():
    streamer_name = get_streamer_name()
    vodID = input("Enter stream ID: ").strip()
    timestamp = input("Enter VOD timestamp (YYYY-MM-DD HH:MM): ").strip()
    recover_vod(streamer_name, vodID, timestamp)

def recover_vod(streamer_name, vodID, timestamp):
    valid_url_list = get_valid_urls(get_all_urls(streamer_name, vodID, timestamp))
    if len(valid_url_list) > 0:
        print(valid_url_list[0])
        if vod_is_muted(valid_url_list[0]):
            print("VOD contains muted segments")
            user_option = input("Would you like to unmute the vod (Y/N): ")
            if user_option.upper() == "Y":
                unmute_vod(valid_url_list[0])
        else:
            print("VOD does NOT contain muted segments")
        user_option = input("Would you like to check if segments are valid (Y/N): ")
        if user_option.upper() == "Y":
            check_segments(valid_url_list[0])
    else:
        print("No VODs found using current domain list.\n"
              "See the following links if you would like to check the other sites: \n")
        for website in generate_website_links(streamer_name, vodID):
            print(website)

def bulk_vod_recovery():
    streamer_name = get_streamer_name()
    file_path = input("Enter full path of sullygnome CSV file: ").replace('"', '')
    for timestamp, vodID in parse_vod_csv_file(file_path).items():
        print("Recovering VOD... ", vodID)
        valid_url_list = get_valid_urls(get_all_urls(streamer_name, vodID, timestamp))
        if len(valid_url_list) > 0:
            print(valid_url_list[0])
            if vod_is_muted(valid_url_list[0]):
                print("VOD contains muted segments")
            else:
                print("VOD does NOT contain muted segments")
        else:
            print("No VODs found using current domain list." + "\n")

def get_valid_clips_urls(clip_list, reps):
    full_url_list, valid_url_list = [], []
    total_counter, valid_counter = 0, 0
    rs = (grequests.head(u) for u in clip_list)
    for result in grequests.imap(rs, size=100):
        total_counter += 1
        full_url_list.append(result.url)
        if total_counter == 500:
            print(str(len(full_url_list)) + " of " + str(round(reps / 2)))
            total_counter = 0
        if result.status_code == 200:
            valid_counter += 1
            valid_url_list.append(result.url)
            print(str(valid_counter) + " Clip(s) Found")
    return valid_url_list

def recover_all_clips():
    streamer_name = get_streamer_name()
    vodID = input("Enter VOD ID: ")
    hours = input("Enter hour value: ")
    minutes = input("Enter minute value: ")
    duration = get_duration(hours, minutes)
    reps = get_reps(duration)
    valid_clips = get_valid_clips_urls(get_all_clip_urls(vodID, reps), reps)
    if len(valid_clips) >= 1:
        user_option = input("Do you want to log results to file (Y/N): ")
        if user_option.upper() == "Y":
            with open(generate_log_filename(get_default_directory(), streamer_name, vodID), "w") as log_file:
                for url in valid_clips:
                    log_file.write(url + "\n")
            log_file.close()
            user_option = input("Do you want to download the recovered clips (Y/N): ")
            if user_option.upper() == "Y":
                download_clips(get_default_directory(), streamer_name, vodID)
            else:
                return
        else:
            return
    else:
        print("No clips found! Returning to main menu.")
        return

def parse_clip_csv_file(file_path):
    vod_info_dict = {}
    csv_file = open(file_path, "r+")
    lines = csv_file.readlines()[1:]
    for line in lines:
        if line.strip():
            filtered_string = line.partition("stream/")[2].replace('"', "")
            vod_id = filtered_string.split(",")[0]
            duration = filtered_string.split(",")[1]
            if vod_id != 0:
                reps = get_reps(int(duration))
                vod_info_dict.update({vod_id: reps})
            else:
                pass
    csv_file.close()
    return vod_info_dict

def parse_vod_csv_file(file_path):
    vod_info_dict = {}
    csv_file = open(file_path, "r+")
    lines = csv_file.readlines()[1:]
    for line in lines:
        if line.strip():
            if len(line.split(",")[1].split(" ")[1]) > 3:
                day = line.split(",")[1].split(" ")[1][:2]
            else:
                day = line.split(",")[1].split(" ")[1][:1]
            month = line.split(",")[1].split(" ")[2]
            year = line.split(",")[1].split(" ")[3]
            timestamp = line.split(",")[1].split(" ")[4]
            stream_datetime = day + " " + month + " " + year + " " + timestamp
            vod_id = line.partition("stream/")[2].split(",")[0].replace('"', "")
            stream_date = datetime.datetime.strftime(
                datetime.datetime.strptime(stream_datetime.strip().replace('"', "") + ":00", "%d %B %Y %H:%M:%S"),
                "%Y-%m-%d %H:%M:%S")
            vod_info_dict.update({stream_date: vod_id})
    csv_file.close()
    return vod_info_dict

def get_random_clips():
    counter = 0
    vod_id = input("Enter VOD ID: ")
    hours = input("Enter Hours: ")
    minutes = input("Enter Minutes: ")
    full_url_list = (get_all_clip_urls(vod_id, get_reps(get_duration(hours, minutes))))
    random.shuffle(full_url_list)
    print("Total Number of URLs: " + str(len(full_url_list)))
    rs = (grequests.head(u) for u in full_url_list)
    for result in grequests.imap(rs, size=100):
        if result.status_code == 200:
            counter += 1
            if counter == 1:
                print(result.url)
                user_option = input("Do you want another URL (Y/N): ")
                if user_option.upper() == "Y":
                    continue
                else:
                    return
        counter = 0

def bulk_clip_recovery():
    vod_counter, total_counter, valid_counter, iteration_counter = 0, 0, 0, 0
    streamer = input("Enter Streamer: ")
    file_path = input("Enter full path of sullygnome CSV file: ").replace('"', '')
    user_option = input("Do you want to download all clips recovered (Y/N)? ")
    for vod, duration in parse_clip_csv_file(file_path).items():
        vod_counter += 1
        print("Processing Twitch VOD... " + str(vod) + " - " + str(vod_counter) + " of " + str(len(parse_clip_csv_file(file_path))))
        original_vod_url_list = get_all_clip_urls(vod, duration)
        rs = (grequests.head(u) for u in original_vod_url_list)
        for result in grequests.imap(rs, size=100):
            total_counter += 1
            iteration_counter += 1
            if total_counter == 500:
                print(str(iteration_counter) + " of " + str(len(original_vod_url_list)))
                total_counter = 0
            if result.status_code == 200:
                valid_counter += 1
                print(str(valid_counter) + " Clip(s) Found")
                with open(generate_log_filename(get_default_directory(), streamer, vod), "a+") as log_file:
                    log_file.write(result.url + "\n")
                log_file.close()
            else:
                continue
        if valid_counter != 0:
            if user_option.upper() == "Y":
                download_clips(get_default_directory(), streamer, vod)
            else:
                print("Recovered clips logged to " + generate_log_filename(get_default_directory(), streamer, vod))
        total_counter, valid_counter, iteration_counter = 0, 0, 0

def download_clips(directory, streamer, vod_id):
    counter = 0
    print("Starting Download....")
    download_directory = directory + "\\" + streamer.title() + "_" + vod_id
    if os.path.exists(download_directory):
        pass
    else:
        os.mkdir(download_directory)
    for links in return_file_contents(directory, streamer, vod_id):
        counter = counter + 1
        if "-offset-" in links:
            clip_offset = links.split("-offset-")[1].replace(".mp4", "")
        else:
            clip_offset = links.split("-index-")[1].replace(".mp4", "")
        link_url = os.path.basename(links)
        r = requests.get(links, stream=True)
        if r.status_code == 200:
            if str(link_url).endswith(".mp4"):
                with open(download_directory + "\\" + streamer.title() + "_" + str(vod_id) + "_" + str(clip_offset) + ".mp4", 'wb') as x:
                    print(datetime.datetime.now().strftime("%Y/%m/%d %I:%M:%S    ") + "Downloading Clip " + str(counter) + " of " + str(len(return_file_contents(directory, streamer, vod_id))) + " - " + links)
                    x.write(r.content)
            else:
                print("ERROR: Please check the log file and failing link!", links)
        else:
            print("ERROR: " + str(r.status_code) + " - " + str(r.reason))
            pass

def run_script():
    print("\n" + "WELCOME TO VOD RECOVERY")
    menu = 0
    while menu < 6:
        return_main_menu()
        menu = int(input("Please choose an option: "))
        if menu == 1:
            recover_live()
        elif menu == 2:
            vod_type = int(input("1) Recover VOD" + "\n" + "2) Recover VODs from SullyGnome export" + "\n" + "Enter what type of VOD recovery: "))
            if vod_type == 1:
                recover_vod_manual()
            elif vod_type == 2:
                bulk_vod_recovery()
            else:
                print("Invalid option! Returning to main menu.")
        elif menu == 3:
            clip_type = int(input("1) Recover all clips from a single VOD" + "\n" + "2) Find random clips from a single VOD" + "\n" + "3) Bulk recover clips from SullyGnome export" + "\n" + "Enter what type of clip recovery: "))
            if clip_type == 1:
                recover_all_clips()
            elif clip_type == 2:
                get_random_clips()
            elif clip_type == 3:
                bulk_clip_recovery()
            else:
                print("Invalid option! Returning to main menu.")
        elif menu == 4:
            url = input("Enter M3U8 Link: ")
            unmute_vod(url)
        elif menu == 5:
            url = input("Enter M3U8 Link: ")
            check_segments(url)
        else:
            print("Exiting...")

run_script()
