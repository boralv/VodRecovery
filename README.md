# VodRecovery
* Created By: ItIckeYd
* Initial Release: May 3rd, 2022
* The script is used to retrieve sub-only and deleted videos from twitch.
* Credits to daylamtayari - [TwitchRecover](https://github.com/TwitchRecover/TwitchRecover) repository helped with the logic to recover twitch videos.

# Script Installation
1. Install Python
2. Clone repository
3. Navigate into cloned directory
4. Install required packages ``` pip install -r requirements.txt ``` (Run in terminal)
5. Run Script :)

# Script Notes
* The script CANNOT recover every single vod. The script can only recover vods that still exist on the twitch vod domains.
* Due to twitch's deletion process vods are typically only available up to 60 days old. The script will notify you if its older then 60 days.
* The script uses UTC timezone as default when recovering vods.
* Ensure to enter the seconds value as 00 when running the script as the script brute forces the seconds value automatically.

# Analytical Sites
* The following sites can be used to provide the information that the script requires:
1. [TwitchTracker.com](https://twitchtracker.com/)
2. [Sullygnome.com](https://sullygnome.com/)
3. [Streamscharts.com](https://streamscharts.com/)

# Optional IDE
* Python has a few code editors that can be used which include the following:
1. PyCharm
2. Visual Studio Code

# Additional Notes
* If creating an issue for a problem that your experiencing please provide atleast 1 example.
* If you are not getting results back from the script. Please try vods from other streamers, if the other streamers vods give you results then the original vods you were trying probably just don't exist. 


# Latest Release
[Stable Release 1.0.1.0](https://github.com/ItIckeYd/VodRecovery/releases/tag/1.0.1.0)

