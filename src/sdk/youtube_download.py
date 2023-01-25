import time 
import streamlit as st
from pathlib import Path 
from pytube import YouTube, StreamQuery
from configs import EnvConfig as env 

class YoutubeDownloader:
    def __init__(self) -> None:
        self.root_dir = Path(env.DATADIR) / 'raw'

    def download(self, url, name_to_save=None):
        self._tube = YouTube(url)
        try:
            video = self._tube.streams.filter(resolution='720p', audio_codec='mp4a.40.2', mime_type='video/mp4').first()
            title = str(name_to_save if name_to_save else video.title) + '.'+ video.subtype
            download_path = self.root_dir / title
            print("=> Downloading...")
            video.download(filename=download_path)
            print("=> Downloading Finished ...")
        except:
            print("=> Retrying...") 
            time.sleep(5)
            self.download(url, name_to_save) 

if __name__ == '__main__':
    tube = YoutubeDownloader()
    tube.download(url='https://www.youtube.com/watch?v=QK0da5WkqG8', name_to_save='wants_and_needs_remix')