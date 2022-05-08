# VodRecovery
* Created By: ItIckeYd
* Initial Release: May 3rd, 2022
* The script is used to retrieve sub-only and deleted videos from twitch.
* Credits to daylamtayari - TwitchRecover repository helped with the logic to recover twitch videos.

# Script Requirements
* MUST have python installed.
* MUST have additional packages installed (ie.. Requests)

# Script Notes
* The script CANNOT recover every single vod. The script can only recover vods that still exist on the twitch vod domains.
* Due to twitch's deletion process vods are typically only available up to 60 day old. The script will notify you if its only then 60 days.
* The script uses local time to return results therefore using values from somebody else's example will not always work.
* Ensure to enter the seconds value as 00 when running the script as the script brute forces the seconds value automatically.

# Analytical Sites
* The following sites can be used to provide the information that the script requires:
1. TwitchTracker.com
2. Sullygnome.com
3. Streamscharts.com

# Optional IDE
* Python has a few code editors that can be used which include the following:
1. PyCharm
2. Visual Studio Code

# Additional Notes
* If creating an issue for a problem that your experiencing please provide atleast 1 example.
* If you are not getting results back from the script. Please try vods from other streamers, if the other streamers vods give you results then the original vods you were trying probably just don't exist. 

