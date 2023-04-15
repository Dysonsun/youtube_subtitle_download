from pytube import YouTube
import yt_dlp
import argparse
import os
import requests
import webvtt
import cv2

class SubtitleGenerator:
    def __init__(self, args):
        self.video_url = args.video_url
        self.video_save_path = args.video_save_path
        self.is_save_cover = args.is_save_cover
        
    def video_download(self):
        # 下载youtube视频
        yt = YouTube(self.video_url)
        title = yt.title
        title = title.replace(" ", "_").replace("|", "").replace(":", "").replace(",", "").replace("?", "")
        self.video_save_path = os.path.join(self.video_save_path, title)
        if not os.path.isdir(self.video_save_path):
            os.makedirs(self.video_save_path)
        # Get the cover URL
        cover_image_save_path = os.path.join(self.video_save_path, 'cover.jpg')
        if not os.path.exists(cover_image_save_path) and self.is_save_cover:
            cover_url = yt.thumbnail_url
            # Download the cover image
            response = requests.get(cover_url)
            with open(cover_image_save_path, "wb") as f:
                f.write(response.content)
            try:
                image_data = cv2.imread(cover_image_save_path)
                image_data = cv2.resize(image_data, (960, 600))
                cv2.imwrite(cover_image_save_path.replace('.jpg', '_re.jpg'), image_data)
            except Exception as e:
                print(e)

        self.download_subs_and_video(self.video_url, ['en', 'en-us', 'zh'])
    
    def download_subs_and_video(self, video_url, lang=[]):
        ydl_opts = {
            'writesubtitles': True,
            'allsubtitles': False,
            'subtitleslangs': lang,
            'subtitlesformat': 'vtt',
            'outtmpl': f"{self.video_save_path}/%(id)s.%(ext)s",
            # 'format': 'mp4',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        for file in os.listdir(self.video_save_path):
            if file.endswith('.vtt'):
                self.convert_vtt_to_srt(os.path.join(self.video_save_path, file),
                                        os.path.join(self.video_save_path, file.replace('.vtt', '.srt')))
        
    def convert_vtt_to_srt(self, vtt_path, srt_path):
        # 打开vtt文件
        print("covert: {}  \n to \n {}".format(vtt_path, srt_path))
        with open(vtt_path, 'r', encoding="utf-8") as f:
            captions = webvtt.read_buffer(f)
        
        srt_captions = ''
        for i, caption in enumerate(captions):
            text = caption.text.strip().replace('&nbsp;', '')
            srt_captions += f"{i+1}\n"
            srt_captions += f"{caption.start} --> {caption.end}\n"
            srt_captions += f"{text}\n\n"

        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write(srt_captions)       
     
    def run(self):
        self.video_download()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video_url", type=str, default="https://youtu.be/wiYCL-sgPDA")
    parser.add_argument("--video_save_path", type=str, default="./videos/musk")
    parser.add_argument("--is_save_cover", type=bool, default=True)
    args = parser.parse_args()
    
    sg = SubtitleGenerator(args)
    sg.run()
    