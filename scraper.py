import os
import time
from requests_html import HTMLSession
from regex import *
import subprocess
import progressbar


class Scraper:
    def __init__(self):
        self.session = HTMLSession()

    def authenticate(self, email, password):
        self.session.get("https://www.alevelphysicsonline.com/")
        model = self.session.get(
            "https://www.alevelphysicsonline.com/_api/v2/dynamicmodel"
        )
        self.session.headers.setdefault(
            "authorization",
            model.json()["apps"]["22bef345-3c5b-4c18-b782-74d4085112ff"]["instance"],
        )
        login = self.session.post(
            "https://www.alevelphysicsonline.com/_api/iam/authentication/v2/login",
            json={
                "loginId": {"email": email},
                "password": password,
                "captchaTokens": [],
            },
        )
        if login.status_code != 200:
            raise Exception("Invalid username or password")

        self.session.post(
            "https://www.alevelphysicsonline.com/_api/iam/cookie/v1/createSessionCookie",
            json={
                "sessionToken": login.json()["sessionToken"],
                "protectedPages": False,
            },
        )

    def get_site_structure(self, url):
        page = self.session.get(url)
        links = filter(lambda l: VIDEO_PAGE_RE.search(l), page.html.links)
        structure = {}
        for link in links:
            video_page = self.session.get(link)
            title = (
                video_page.html.find("title", first=True)
                .text.removesuffix(" - A Level Physics Online")
                .strip()
            )

            unique_links = set(
                filter(lambda l: not l.endswith(".pdf"), video_page.html.links)
            )
            for link in page.html.links:
                if link in unique_links:
                    unique_links.remove(link)
            print(f"{title}: discovered {len(unique_links)} links")
            structure[title] = list(unique_links)

        return structure

    def get_video_urls(self, url):
        page = self.session.get(url)
        pre_scripts = []
        subtopic = (
            page.html.find("title", first=True)
            .text.removesuffix(" | A Level Physics Online")
            .strip()
        )

        for link in page.html.find("link"):
            if not PRE_SCRIPT_URL_RE.search(link.attrs["href"]):
                continue
            pre_scripts.append(link.attrs["href"].replace("®", "&reg"))

        vimeo_urls = []
        for script in pre_scripts:
            res = self.session.get(script)
            vimeo_urls += VIMEO_URL_RE.findall(res.text)

        videos = []

        for url in vimeo_urls:
            iframe = self.session.get(
                url.replace("vimeo.com", "player.vimeo.com/video"),
                headers={"Referer": "https://www.alevelphysicsonline.com/"},
            )
            matches = MASTER_URL_RE.findall(iframe.text)

            if len(matches) == 0:
                continue

            videos.append(
                (
                    iframe.html.find("title", first=True)
                    .text.removesuffix(" on Vimeo")
                    .removesuffix(".mp4")
                    .strip(),
                    matches[0] + "?query_string_ranges=1",
                ),
            )
        return subtopic, videos

    def download_video(self, master_url, out_file):
        print(f"Downloading {out_file}")
        base_url = BASE_URL_RE.findall(master_url)[0]
        data = self.session.get(master_url).json()

        video_blob = sorted(data["video"], key=lambda p: p["width"])[-1]

        audio_blob = sorted(
            filter(lambda p: p["format"] == video_blob["format"], data["audio"]),
            key=lambda p: p["bitrate"],
        )[-1]

        print(f"Video quality: {video_blob['height']}x{video_blob['height']}")
        print(f"Audio bitrate: {round(audio_blob['bitrate']/1000)} kbps")

        video_file = data["clip_id"] + "_video.mp4"
        audio_file = data["clip_id"] + "_audio.mp4"

        video_url = ""
        audio_url = ""
        if video_blob["format"] == "mp42":
            video_url = base_url + "/sep/video/" + video_blob["base_url"]
            audio_url = base_url + "/sep/audio/" + video_blob["base_url"]
        elif video_blob["format"] == "dash":
            video_url = base_url + "/parcel/video/"
            audio_url = base_url + "/parcel/audio/"
        else:
            raise Exception(f"Unknown video format: {video_blob['format']}")

        print("Downloading video segments...")
        self.__download_bundle(video_url, video_blob, video_file)
        print("Downloading audio segments...")
        self.__download_bundle(audio_url, audio_blob, audio_file)

        print("Merging files...")
        subprocess.run(
            f"ffmpeg -loglevel quiet -y -i {video_file} -i {audio_file} -c copy {out_file}"
        )
        os.remove(video_file)
        os.remove(audio_file)
        print(f"Downloaded {out_file}")

    def __download_bundle(self, base_url, blob, out_file):
        try:
            os.remove(out_file)
        except FileNotFoundError:
            pass

        file = open(out_file, "ab+")

        total_size = sum([seg["size"] for seg in blob["segments"]])
        bar = progressbar.ProgressBar(max_value=total_size)

        for key in ("init_segment", "index_segment"):
            if blob.get(key) is not None:
                res = self.session.get(base_url + blob[key])
                file.write(res.content)
                bar.print(f"Fetched {key}")

        total_downloaded = 0

        for i, segment in enumerate(blob["segments"]):
            res = self.session.get(base_url + segment["url"])
            if res.status_code == 200:
                file.write(res.content)
                total_downloaded += segment["size"]
                bar.update(total_downloaded)
                continue
            print(f"packet {i} failed: {res.status_code}")
            time.sleep(3)

        file.close()
        progressbar.streams.flush()
        print()
