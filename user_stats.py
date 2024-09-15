import requests
def get_user_stats(username):
    content = requests.get(f"https://lichess.org/api/user/{username}")
    if content.status_code == 200:
        all_stats = content.json()
        print(all_stats)
        wanted_stats = {}
        if "disabled" in all_stats and all_stats["disabled"] == True:
            return None
        if "title" in all_stats:
            wanted_stats["title"] = all_stats["title"]
        wanted_stats["username"] = all_stats["username"]
             
        for ratings in all_stats["perfs"]:
            if ratings in ["bullet", "blitz", "rapid", "classical"]:
                wanted_stats[f"{ratings}_rating"] = all_stats["perfs"][ratings]["rating"]
        return wanted_stats
