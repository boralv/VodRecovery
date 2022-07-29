import random
import datetime
from datetime import datetime
import datetime
import hashlib
from concurrent.futures import ThreadPoolExecutor
import os
import grequests
import requests

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
    print("WELCOME TO VOD RECOVERY" + "\n")
    menu = "1) Recover Vod" + "\n" + "2) Recover Clips" + "\n" + "3) Unmute an M3U8 file" + "\n" + "4) Check M3U8 Segments" + "\n" + "5) Exit" + "\n"
    print(menu)

def return_request_response(url):
    return requests.get(url)

def return_request_head(url):
    return requests.head(url)

def check_user_response(user_bool):
    return bool(user_bool.upper() == "Y")

def check_status_code(status_code):
    return bool(status_code == 200)

def get_default_directory():
    default_directory = os.path.expanduser("~\\Documents\\")
    return default_directory

def get_file_directory(directory, streamer, vod_id):
    file_path = os.path.join(directory+"\\"+streamer+"_"+vod_id + "_log.txt")
    return file_path

def generate_vod_filename(streamer, vod_id):
    unmuted_file_name = get_default_directory()+"VodRecovery_"+streamer+ "_"+ vod_id+".m3u8"
    return unmuted_file_name

def remove_file(file_path):
    if os.path.exists(file_path):
        return os.remove(file_path)

def format_timestamp(timestamp):
    formatted_date = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    return formatted_date

def get_vod_age(timestamp):
    return datetime.datetime.today() - format_timestamp(timestamp)

def load_response_content(url):
    return return_request_response(url).text

def parse_m3u8_link(url):
    streamer = url.split("_")[1]
    vod_id = url.split("_")[3].split("/")[0]
    return streamer,vod_id

def get_all_urls(streamer, vod_id, vod_timestamp):
    urls = []
    for bf_second in range(60):
        converted_timestamp = (datetime.datetime(format_timestamp(vod_timestamp).year,format_timestamp(vod_timestamp).month,format_timestamp(vod_timestamp).day,format_timestamp(vod_timestamp).hour,format_timestamp(vod_timestamp).minute,bf_second) - datetime.datetime(1970,1,1)).total_seconds()
        base_url = streamer + "_" + vod_id + "_" + str(int(converted_timestamp))
        hashed_base_url = str(hashlib.sha1(base_url.encode('utf-8')).hexdigest())[:20]
        formatted_base_url = hashed_base_url + '_' +  base_url
        for domain in domains:
            url = domain+formatted_base_url+"/chunked/index-dvr.m3u8"
            urls.append(url)
    return urls

def get_valid_urls(url_list):
    valid_url_list = []
    rs = (grequests.head(u) for u in url_list)
    for result in grequests.imap(rs, size=100):
        if check_status_code(result.status_code):
            valid_url_list.append(result.url)
    return valid_url_list

def bool_is_muted(url):
    return bool("unmuted" in load_response_content(url))

def write_vod_file(url,file_path):
    vod_file = open(file_path, "w")
    vod_file.write(load_response_content(url))
    vod_file.close()

def unmute_vod(url,file_path):
    list_of_lines = []
    write_vod_file(url, file_path)
    vod_file = open(file_path, "r")
    for lines in vod_file.readlines():
        list_of_lines.append(lines)
    vod_file.close()
    counter = 0
    with open(file_path, "w") as unmuted_vod_file:
        for segment in list_of_lines:
            url = url.replace("index-dvr.m3u8", "")
            if "-unmuted" in segment and not segment.startswith("#"):
                counter += 1
                unmuted_vod_file.write(segment.replace(segment, str(url) + str(counter - 1)) + "-muted.ts" + "\n")
            elif "-unmuted" not in segment and not segment.startswith("#"):
                counter += 1
                unmuted_vod_file.write(segment.replace(segment, str(url) + str(counter - 1)) + ".ts" + "\n")
            else:
                 unmuted_vod_file.write(segment)
    unmuted_vod_file.close()
    print(os.path.basename(file_path)+" Has been unmuted. File can be found in " + file_path)

def unmute_user_m3u8(url):
    streamer = parse_m3u8_link(url)[0]
    vod_id = parse_m3u8_link(url)[1]
    list_of_lines = []
    write_vod_file(url, generate_vod_filename(streamer,vod_id))
    vod_file = open(generate_vod_filename(streamer,vod_id), "r")
    for lines in vod_file.readlines():
        list_of_lines.append(lines)
    vod_file.close()
    counter = 0
    with open(generate_vod_filename(streamer,vod_id), "w") as unmuted_vod_file:
        for segment in list_of_lines:
            url = url.replace("index-dvr.m3u8", "")
            if "-unmuted" in segment and not segment.startswith("#"):
                counter += 1
                unmuted_vod_file.write(segment.replace(segment, str(url) + str(counter - 1)) + "-muted.ts" + "\n")
            elif "-unmuted" not in segment and not segment.startswith("#"):
                counter += 1
                unmuted_vod_file.write(segment.replace(segment, str(url) + str(counter - 1)) + ".ts" + "\n")
            else:
                unmuted_vod_file.write(segment)
    unmuted_vod_file.close()
    print(os.path.basename(generate_vod_filename(streamer,vod_id)) + " Has been unmuted. File can be found in " + generate_vod_filename(streamer,vod_id))

def get_segments(url, file_path):
    list_of_lines,segment_list = [],[]
    counter = 0
    if os.path.exists(file_path):
        with open(file_path, "r+") as unmuted_vod_file:
            for segment in unmuted_vod_file.readlines():
                url = url.replace("index-dvr.m3u8", "")
                if "-muted" in segment and not segment.startswith("#"):
                    counter += 1
                    segment_list.append(str(url) + str(counter - 1) + "-muted.ts")
                elif "-muted" not in segment and not segment.startswith("#"):
                    counter += 1
                    segment_list.append(str(url) + str(counter - 1) + ".ts")
                else:
                    pass
        unmuted_vod_file.close()
    else:
        write_vod_file(url, file_path)
        vod_file = open(file_path, "r")
        for lines in vod_file.readlines():
            list_of_lines.append(lines)
        vod_file.close()
        counter = 0
        with open(file_path, "w") as unmuted_vod_file:
            for segment in list_of_lines:
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
        if check_status_code(result.status_code):
            valid_segment_counter +=1
    return valid_segment_counter

def recover_vod():
    streamer_name = input("Enter streamer name: ").lower().strip()
    vodID = input("Enter vod id: ").strip()
    timestamp = input("Enter VOD timestamp (YYYY-MM-DD HH:MM:SS): ").strip()
    print("Vod is " + str(get_vod_age(timestamp).days) + " days old. If the vod is older than 60 days chances of recovery are slim." + "\n")
    url_list = get_valid_urls(get_all_urls(streamer_name, vodID, timestamp))
    if len(url_list) > 0:
        first_url_index = url_list[0]
        if bool_is_muted(first_url_index):
            print(first_url_index)
            print("Vod contains muted segments")
            bool_unmute_vod = input("Would you like to unmute the vod (Y/N): ")
            if check_user_response(bool_unmute_vod):
                unmute_vod(first_url_index, generate_vod_filename(streamer_name, vodID))
                print("Total Number of Segments: " + str(len(get_segments(first_url_index, generate_vod_filename(streamer_name,vodID)))))
                check_segment = input("Would you like to check if segments are valid (Y/N): ")
                if check_user_response(check_segment):
                    print(str(check_segment_availability(get_segments(first_url_index, generate_vod_filename(streamer_name,vodID))))+ " of " + str(len(get_segments(first_url_index, generate_vod_filename(streamer_name,vodID)))) + " segments are valid.")
        else:
            print(first_url_index)
            print("Vod does NOT contain muted segments")
            print("Total Number of Segments: " + str(len(get_segments(first_url_index, generate_vod_filename(streamer_name, vodID)))))
            check_segment = input("Would you like to check if segments are valid (Y/N): ")
            if check_user_response(check_segment):
                print(str(check_segment_availability(get_segments(first_url_index, generate_vod_filename(streamer_name, vodID)))) + " of " + str(len(get_segments(first_url_index,generate_vod_filename(streamer_name, vodID)))) + " segments are valid.")
            if os.path.exists(generate_vod_filename(streamer_name,vodID)):
                remove_file(generate_vod_filename(streamer_name,vodID))
            else:
                pass
    else:
        print("No vods found using current domain list." + "\n")


def get_duration(hours, minutes):
    return (int(hours) * 60) + int(minutes)

def get_reps(duration):
    reps = ((duration * 60) + 2000) * 2
    return reps

def get_all_clip_urls(vod_id, reps):
    original_vod_url_list = ["https://clips-media-assets2.twitch.tv/" + vod_id + "-offset-" + str(i) + ".mp4" for i in
                             range(reps) if i % 2 == 0]
    return original_vod_url_list

def get_valid_clips_urls(clip_list, reps):
    full_url_list,valid_url_list = [],[]
    total_counter,valid_counter = 0,0
    rs = (grequests.head(u) for u in clip_list)
    for result in grequests.imap(rs, size=100):
        total_counter +=1
        full_url_list.append(result.url)
        if total_counter == 500:
            print(str(len(full_url_list)) + " of " + str(round(reps / 2)))
            total_counter = 0
        if check_status_code(result.status_code):
            valid_counter += 1
            valid_url_list.append(result.url)
            print(str(valid_counter) + " Clip(s) Found")
    return valid_url_list

def recover_all_clips():
    streamer_name = input("Enter streamer name: ").lower().strip()
    vodID = input("Enter vod id: ").strip()
    hours = input("Enter hour value: ")
    minutes = input("Enter minute value: ")
    duration = get_duration(hours,minutes)
    reps = get_reps(duration)
    valid_clips = get_valid_clips_urls(get_all_clip_urls(vodID,reps), reps)
    log_file = input("Do you want to log results to file (Y/N): ")
    if check_user_response(log_file):
        file_name = get_file_directory(get_default_directory(), streamer_name, vodID)
        log = open(file_name, "a")
        for url in valid_clips:
            log.write(url + "\n")
        log.close()
        bool_download = input("Do you want to download the recovered clips (Y/N): ")
        if check_user_response(bool_download):
            download_clips(get_default_directory(), streamer_name, vodID)
        else:
            return
    else:
        return

def return_file_contents(directory, streamer, vod_id):
    with open(get_file_directory(directory, streamer, vod_id)) as f:
        content = f.readlines()
        content = [x.strip() for x in content]
    return content

def parse_csv_file(file_path):
    vod_info_dict = {}
    csv_file = open(file_path, "r+")
    lines = csv_file.readlines()[1:]
    for line in lines:
        if line.strip():
            filtered_string = line.partition("stream/")[2]
            final_string = filtered_string.split(",")
            if int(final_string[1]) != 0:
                reps = ((int(final_string[1]) * 60) + 2000) * 2
                vod_info_dict.update({final_string[0]: reps})
            else:
               pass
    csv_file.close()
    return vod_info_dict

def get_random_clips():
    vod_id = input("Enter vod id: ")
    hours = input("Enter Hours: ")
    minutes = input("Enter Minutes: ")
    full_url_list = (get_all_clip_urls(vod_id,get_reps(get_duration(hours,minutes))))
    random.shuffle(full_url_list)
    print("Total Number of Urls: " + str(len(full_url_list)))
    with ThreadPoolExecutor(max_workers=100) as pool:
        url_list = []
        max_url_list_length = 500
        current_list = full_url_list
        for i in range(0, len(full_url_list), max_url_list_length):
            batch = current_list[i:i + max_url_list_length]
            response_list = list(pool.map(return_request_head, batch))
            for index, elem in enumerate(response_list):
                url_list.append(elem)
                if check_status_code(elem.status_code):
                    print(elem.url)
                    next_url = input("Do you want another url (Y/N): ")
                    if check_user_response(next_url):
                        if check_status_code(response_list[index + 1].status_code):
                            print(response_list[index + 1].url)
                    else:
                        return

def bulk_clip_recovery():
    vod_counter,total_counter, valid_counter, iteration_counter = 0,0,0,0
    streamer = input("Enter Streamer: ").lower()
    file_path = input("Enter full path of sullygnome CSV file: ")
    for vod, duration in parse_csv_file(file_path).items():
        vod_counter += 1
        print("Processing Twitch Vod... " + str(vod) + " - " + str(vod_counter) + " of " + str(len(parse_csv_file(file_path))))
        original_vod_url_list = get_all_clip_urls(vod,duration)
        rs = (grequests.head(u) for u in original_vod_url_list)
        for result in grequests.imap(rs, size=100):
            total_counter +=1
            iteration_counter += 1
            if total_counter == 500:
                print(str(iteration_counter) + " of " + str(len(original_vod_url_list)))
                total_counter = 0
            if check_status_code(result.status_code):
                valid_counter += 1
                print(str(valid_counter) + " Clip(s) Found")
                file_name = get_default_directory() + "\\" + streamer + "_" + vod + "_log.txt"
                log = open(file_name, "a+")
                log.write(result.url + "\n")
                log.close()
            else:
               continue
        if valid_counter != 0:
            bool_download = input("Do you want to download the recovered clips (Y/N): ")
            if check_user_response(bool_download):
                download_clips(get_default_directory(), streamer, vod)
            else:
                print("Recovered clips logged to " + get_file_directory(get_default_directory(), streamer, vod))
        total_counter,valid_counter,iteration_counter = 0,0,0

def download_clips(directory, streamer, vod_id):
    counter = 0
    print("Starting Download....")
    download_directory = directory+"\\"+streamer.title()+"_"+vod_id
    if os.path.exists(download_directory):
        pass
    else:
        os.mkdir(download_directory)
    for links in return_file_contents(directory, streamer, vod_id):
        counter = counter + 1
        vod_counter = links.split("-offset-")[1].replace(".mp4","")
        link_url = os.path.basename(links)
        r = requests.get(links, stream=True)
        if check_status_code(r.status_code):
            if str(link_url).endswith(".mp4"):
                with open(download_directory+"\\"+streamer.title()+"_" + str(vod_id) + "_" + str(vod_counter) + ".mp4", 'wb') as x:
                    print(datetime.datetime.now().strftime("%Y/%m/%d %I:%M:%S    ") + "Downloading... Clip " + str(
                        counter) + " of " + str(len(return_file_contents(directory, streamer, vod_id))) + " - " + links)
                    x.write(r.content)
            else:
                print("ERROR: Please check the log file and failing link!", links)
        else:
            print("ERROR: " + str(r.status_code) + " - " + str(r.reason))
            pass

def run_script():
    menu = 0
    while menu < 5:
        return_main_menu()
        menu = int(input("Please choose an option: "))
        if menu == 5:
            exit()
        elif menu == 1:
            recover_vod()
        elif menu == 2:
            clip_type = int(input("Enter what type of clip recovery: " + "\n" +"1) Recover all clips from a single VOD" + "\n" + "2) Find random clips from a single VOD" + "\n" + "3) Bulk recover clips from SullyGnome export" + "\n"))
            if clip_type == 1:
                recover_all_clips()
            elif clip_type == 2:
                get_random_clips()
            elif clip_type == 3:
                bulk_clip_recovery()
            else:
                print("Invalid option! Returning to main menu.")
        elif menu == 3:
            url = input("Enter M3U8 Link: ")
            if bool_is_muted(url):
                unmute_user_m3u8(url)
            else:
                print("Vod does NOT contain muted segments")
        elif menu == 4:
            url = input("Enter M3U8 Link: ")
            streamer = parse_m3u8_link(url)[0]
            vod_id = parse_m3u8_link(url)[1]
            print(str(check_segment_availability(get_segments(url, generate_vod_filename(streamer, vod_id)))) + " of " + str(len(get_segments(url,generate_vod_filename(streamer, vod_id)))) + " segments are valid.")
            remove_file(generate_vod_filename(streamer, vod_id))
        else:
            print("Invalid Option! Exiting...")

run_script()
