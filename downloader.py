import os
import subprocess
import queue
import threading
import time
import yt_dlp  # Menggunakan yt-dlp untuk mendapatkan judul video

# Inisialisasi antrian
download_queue = queue.Queue()
current_download = {"type": None, "title": None}  # Status download yang sedang berlangsung

# Fungsi untuk mendapatkan judul video dari URL
def get_video_title(url):
    try:
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'force_generic_extractor': False
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            if not info_dict or 'title' not in info_dict:
                return None
            return info_dict['title']
    except Exception as e:
        print(f"\n[ERROR] Gagal mendapatkan judul dari URL {url}: {e}")
        return None

# Fungsi untuk mendapatkan informasi playlist
def get_playlist_info(url):
    try:
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'force_generic_extractor': False
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            if 'entries' in info_dict:
                return {
                    'title': info_dict.get('title', 'Unknown Playlist'),
                    'videos': [
                        {'url': entry['url'], 'title': entry.get('title', 'Unknown Title')}
                        for entry in info_dict['entries'] if entry
                    ]
                }
            return None
    except Exception as e:
        print(f"\n[ERROR] Gagal mendapatkan informasi playlist: {e}")
        return None

# Fungsi untuk mengunduh video menggunakan subprocess
def download_video(url, download_path='./downloads', title=None):
    os.makedirs(download_path, exist_ok=True)
    try:
        subprocess.run(
            [
                "yt-dlp",
                "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
                "-o", os.path.join(download_path, "%(title)s.%(ext)s"),
                url,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"\n[INFO] Video '{title}' berhasil diunduh.")
    except Exception as e:
        print(f"\n[ERROR] Terjadi kesalahan saat mengunduh video '{title}': {e}")

# Fungsi untuk mengunduh audio menggunakan subprocess
def download_audio(url, download_path='./downloads', format='mp3', title=None):
    os.makedirs(download_path, exist_ok=True)
    try:
        subprocess.run(
            [
                "yt-dlp",
                "-f", "bestaudio[ext=m4a]",
                "-o", os.path.join(download_path, f"%(title)s.{format}"),
                url,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"\n[INFO] Audio '{title}' berhasil diunduh.")
    except Exception as e:
        print(f"\n[ERROR] Terjadi kesalahan saat mengunduh audio '{title}': {e}")

# Fungsi untuk mengunduh playlist
def download_playlist(url, download_path='./downloads'):
    playlist_info = get_playlist_info(url)
    if not playlist_info:
        print("\n[ERROR] URL bukan merupakan playlist yang valid")
        return

    playlist_path = os.path.join(download_path, playlist_info['title'])
    os.makedirs(playlist_path, exist_ok=True)
    
    total_videos = len(playlist_info['videos'])
    print(f"\n[INFO] Menambahkan {total_videos} video dari playlist '{playlist_info['title']}' ke antrian")
    
    for video in playlist_info['videos']:
        download_queue.put({
            'type': 'video',
            'url': video['url'],
            'path': playlist_path,
            'title': video['title']
        })

# Fungsi untuk memproses antrian
def process_queue():
    while True:
        if not download_queue.empty():
            item = download_queue.get()
            current_download["type"] = item["type"]
            current_download["title"] = item["title"]
            if item["type"] == "video":
                download_video(item["url"], item.get('path', './downloads'), title=item["title"])
            elif item["type"] == "audio":
                download_audio(item["url"], item.get('path', './downloads'), format=item.get('format', 'mp3'), title=item["title"])
            current_download["type"] = None
            current_download["title"] = None
            download_queue.task_done()
        else:
            time.sleep(1)

# Fungsi untuk menangani input pengguna di thread terpisah
def get_default_download_path():
    """Get the default download path based on the environment"""
    if os.path.exists('/data/data/com.termux/files/home/storage/downloads'):
        # We're in Termux
        return '/data/data/com.termux/files/home/storage/downloads/youtube_downloads'
    return './downloads'

def handle_input():
    while True:
        print("\nPilihan:")
        print("1. Download video")
        print("2. Download audio")
        print("3. Download playlist")
        print("4. Tampilkan status")
        print("5. Keluar")
        
        choice = input("\nMasukkan pilihan (1-5): ")
        
        if choice == '5':
            print("\n[INFO] Menutup program...")
            os._exit(0)
            
        if choice == '4':
            show_status()
            continue
            
        url = input("Masukkan URL YouTube: ")
        default_path = get_default_download_path()
        print(f"\nDefault download path: {default_path}")
        download_path = input(f"Masukkan path download (tekan Enter untuk default '{default_path}'): ") or default_path
        
        if choice == '1':
            title = get_video_title(url)
            if title:
                download_queue.put({
                    'type': 'video',
                    'url': url,
                    'path': download_path,
                    'title': title
                })
                print(f"\n[INFO] Video '{title}' ditambahkan ke antrian")
        
        elif choice == '2':
            title = get_video_title(url)
            if title:
                format = input("Masukkan format audio (mp3/m4a, default: mp3): ") or 'mp3'
                download_queue.put({
                    'type': 'audio',
                    'url': url,
                    'path': download_path,
                    'format': format,
                    'title': title
                })
                print(f"\n[INFO] Audio '{title}' ditambahkan ke antrian")
        
        elif choice == '3':
            download_playlist(url, download_path)
        
        else:
            print("\n[ERROR] Pilihan tidak valid!")

# Fungsi untuk menampilkan status antrian
def show_status():
    if current_download["title"]:
        print(f"\n[STATUS] Sedang mengunduh: {current_download['title']} ({current_download['type']})")
    else:
        print("\n[STATUS] Tidak ada unduhan yang sedang berlangsung.")
    
    if not download_queue.empty():
        print("\n[ANTRIAN] URL yang menunggu:")
        for idx, item in enumerate(list(download_queue.queue), start=1):
            print(f"  {idx}. {item['title']} ({item['type']})")
    else:
        print("\n[ANTRIAN] Tidak ada URL di antrian.")

# Fungsi utama
def main():
    # Menjalankan thread untuk memproses antrian
    threading.Thread(target=process_queue, daemon=True).start()
    # Menjalankan thread untuk menangani input
    threading.Thread(target=handle_input, daemon=False).start()

if __name__ == "__main__":
    main()
