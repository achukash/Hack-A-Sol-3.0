import requests
def get_user_stats(username):
    content = requests.get(f"https://lichess.org/api/user/{username}")
    if content.status_code == 200:
        all_stats = content.json()
        print(all_stats)
        wanted_stats = {}
        if "title" in all_stats:
            wanted_stats["title"] = all_stats["title"]
        wanted_stats["username"] = all_stats["username"]
        wanted_stats["url"] = all_stats["url"]
        if "profile" in all_stats:  
            wanted_stats["flag_url"] = "https://flagsapi.com/" + all_stats["profile"]["flag"] + "/flat/64.png"
        for ratings in all_stats["perfs"]:
            if ratings in ["bullet", "blitz", "rapid", "classical"]:
                wanted_stats[f"{ratings}_rating"] = all_stats["perfs"][ratings]["rating"]
                
        print(wanted_stats)
