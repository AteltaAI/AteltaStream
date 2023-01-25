import os  
import streamlit as st 
from pathlib import Path 
from pytube import YouTube 
from configs import EnvConfig as env
from src.sdk.preprocess_stream import StreamerPreprocess
from src.sdk.two_video_stream import TwoVideoStreamer
from src.sdk.youtube_download import YoutubeDownloader

class StreamlitApp:
    def __init__(self) -> None: 
        self.data_dir = Path(env.DATADIR) / 'processed'
        st.title('AteltaStream')
        st.sidebar.image("assets/icon2.png", use_column_width=True)
        st.text('Where AI meets the drill')
    
    def about_project(self):
        with open('README.md') as f:
            contents = f.read()
            st.image("assets/banner.png")
        st.markdown('\n')
        st.markdown(contents[130:])
        #st.markdown(contents, unsafe_allow_html=True)

    def upload(self):
        
        mode = st.selectbox('Upload/download from youtube', ['Upload Locally', 'Download from YouTube'])
        if mode == 'Download from YouTube':
            link = st.text_input(label="Enter the youtube link to download")
            name_to_save = st.text_input(label="Give a short name of the video to save it")

            if link and name_to_save:
                st.markdown("##### `Downloading started ...` ✨")
                tube = YoutubeDownloader()
                tube.download(link, name_to_save)
                st.markdown("##### `Downloading Finished` 🥳, `Starting to Process` ⚙")
                streamer = StreamerPreprocess(source_to_process=f'raw/{name_to_save}.mp4')
                status = streamer.pre_process(st=True) 
                if status:
                    st.balloons()
                    st.markdown("#### `Processing finished` 🥳")
        else:
            uploader = st.text_input('Enter the file location of the video')
            if uploader:
                st.markdown("#### `Processing started ...`")
                streamer = StreamerPreprocess(source_to_process=uploader)
                status = streamer.pre_process(st=True) 
                if status:
                    st.balloons()
                    st.markdown("#### `Processing finished` 🥳")

    def webapp(self):
        st.markdown('#### Real time streaming and pose evaluation')
        available_video_names = [dir for dir in os.listdir(str(self.data_dir)) if not dir.startswith('.')]
        video_choice = st.sidebar.selectbox("Select the video to practice", available_video_names)
        print(video_choice)
        # let default cam source be 0 
        TwoVideoStreamer(instruction_video_name=video_choice, source_to_stream=0).stream_video_to_app()

    def start(self):
        activities = ["About", "Add new video", "Demo"]
        choice = st.sidebar.selectbox("Navigate", activities)

        if choice == 'About':
            self.about_project()
        elif choice == 'Add new video':
            self.upload()
        else:
            self.webapp()

if __name__ == "__main__":
    app = StreamlitApp().start()