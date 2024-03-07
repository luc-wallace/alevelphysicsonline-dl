import os
from scraper import Scraper
import json

scraper = Scraper()

username = input("Enter alevelphysicsonline email: ")
password = input("Enter alevelphysicsonline password: ")
scraper.authenticate(username, password)

structure = {}


def get_structure():
    structure = {}
    if os.path.isfile("structure.json"):
        with open("structure.json", "r") as file:
            try:
                structure = json.load(file)
            except json.JSONDecodeError:
                print("Invalid structure file")
            else:
                print("Loaded structure.json file")
    if structure == {}:
        print("Fetching page structure...")
        structure = scraper.get_site_structure(
            "https://www.alevelphysicsonline.com/aqa"
        )
        with open("structure.json", "w") as file:
            json.dump(structure, file)
    return structure


structure = get_structure()
for sector, links in structure.items():
    sector_dir_name = sector.replace(" ", "_")
    try:
        os.mkdir(sector_dir_name)
    except:
        pass
    for link in links:
        subtopic, videos = scraper.get_video_urls(link)
        subtopic_dir_name = f"{sector_dir_name}/{subtopic.replace(' ', '_')}"
        try:
            os.mkdir(subtopic_dir_name)
        except:
            pass
        for name, url in videos:
            file_name = subtopic_dir_name + f"/{name.replace(' ', '_')}.mp4"
            if os.path.isfile(file_name):
                # file already exists
                continue
            scraper.download_video(url, file_name)
