import os
import subprocess
import queue
import threading
import time
import yt_dlp
from datetime import datetime, timedelta

# Inisialisasi antrian dan status download
download_queue = queue.Queue()
current_download = {
    "type": None, 
    "title": None,
    "progress": 0,
    "total_bytes": 0,
    "downloaded_bytes": 0,
    "speed": "",
    "eta": "",
    "path": None
}

# Variabel untuk mengontrol program
last_activity = datetime.now()
IDLE_TIMEOUT = 300  # 5 menit dalam detik
program_running = True

def update_activity():
    global last_activity
    last_activity = datetime.now()

def check_idle_timeout():
    global program_running
    while program_running:
        if (datetime.now() - last_activity).total_seconds() > IDLE_TIMEOUT:
            if current_download["type"] is None and download_queue.empty():
                print("\n[INFO] Program tidak aktif selama 5 menit. Menutup program...")
                program_running = False
                os._exit(0)
        time.sleep(10)  # Cek setiap 10 detik

# Hook untuk progress callback
def my_hook(d):
    if d['status'] == 'downloading':
        try:
            # Get downloaded bytes
            downloaded = d.get('downloaded_bytes', 0)
            if downloaded == 0:
                downloaded = d.get('downloaded_bytes_str', '0').replace('KiB', '').replace('MiB', '').strip()
                try:
                    downloaded = float(downloaded)
                except:
                    downloaded = 0
            
            # Get total bytes
            total = d.get('total_bytes', 0)
            if total == 0:
                total = d.get('total_bytes_str', '0').replace('KiB', '').replace('MiB', '').strip()
                try:
                    total = float(total)
                except:
                    total = 0
            
            # Get speed
            speed = d.get('speed', 0)
            if speed == 0:
                speed_str = d.get('_speed_str', '0KiB/s').replace('KiB/s', '').replace('MiB/s', '').strip()
                try:
                    speed = float(speed_str)
                except:
                    speed = 0
            
            # Get ETA
            eta = d.get('eta', 0)
            if eta == 0:
                eta_str = d.get('_eta_str', '00:00').replace(':', '')
                try:
                    eta = int(eta_str)
                except:
                    eta = 0
            
            # Update current download info
            current_download['downloaded_bytes'] = downloaded
            current_download['total_bytes'] = total
            current_download['speed'] = speed
            current_download['eta'] = eta
            
            # Calculate progress
            if total > 0:
                current_download['progress'] = (downloaded / total) * 100
            else:
                # Try to get progress from _percent_str
                percent_str = d.get('_percent_str', '0%').replace('%', '').strip()
                try:
                    current_download['progress'] = float(percent_str)
                except:
                    current_download['progress'] = 0
                    
        except Exception as e:
            print(f"Error in progress hook: {str(e)}")
            pass

# Fungsi untuk mendapatkan judul video dari URL
def get_video_title(url):
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            return info_dict.get('title')
    except Exception as e:
        error_msg = str(e).split('\n')[0]
        print(f"\n[ERROR] Gagal mendapatkan judul: {error_msg}")
        return None

# Fungsi untuk mendapatkan informasi playlist
def get_playlist_info(url):
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            if 'entries' in info_dict:
                videos = []
                for entry in info_dict['entries']:
                    if entry and 'id' in entry:
                        videos.append({
                            'url': entry['id'],
                            'title': entry.get('title', 'Unknown Title')
                        })
                return {
                    'title': info_dict.get('title', 'Unknown Playlist'),
                    'videos': videos
                }
            return None
    except Exception as e:
        error_msg = str(e).split('\n')[0]
        print(f"\n[ERROR] Gagal mendapatkan informasi playlist: {error_msg}")
        return None

def get_video_ydl_opts(download_path, title=None):
    return {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',  # Try combined format first, then fallback
        'merge_output_format': 'mp4',  # Force output to mp4
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s') if not title else os.path.join(download_path, f'{title}.%(ext)s'),
        'progress_hooks': [my_hook],
        'quiet': True,
        'no_warnings': True,
        'noprogress': True,  # Disable progress output to console
    }

def get_audio_ydl_opts(download_path, format='mp3', title=None):
    return {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s') if not title else os.path.join(download_path, f'{title}.%(ext)s'),
        'progress_hooks': [my_hook],
        'quiet': True,
        'no_warnings': True,
        'noprogress': True,  # Disable progress output to console
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': format,
            'preferredquality': '192',
        }],
    }

def download_video(url, download_path='./downloads', title=None):
    try:
        os.makedirs(download_path, exist_ok=True)
        ydl_opts = get_video_ydl_opts(download_path, title)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        error_msg = str(e).split('\n')[0]
        if 'format' in error_msg.lower():
            # If format error, try with simpler format
            try:
                ydl_opts['format'] = 'best'
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                return True
            except Exception as e2:
                error_msg = str(e2).split('\n')[0]
                print(f"\n[ERROR] Gagal mengunduh video: {error_msg}")
                return False
        else:
            print(f"\n[ERROR] Gagal mengunduh video: {error_msg}")
            return False

def download_audio(url, download_path='./downloads', format='mp3', title=None):
    try:
        os.makedirs(download_path, exist_ok=True)
        ydl_opts = get_audio_ydl_opts(download_path, format, title)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        error_msg = str(e).split('\n')[0]
        if 'format' in error_msg.lower():
            # If format error, try with simpler format
            try:
                ydl_opts['format'] = 'best'
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                return True
            except Exception as e2:
                error_msg = str(e2).split('\n')[0]
                print(f"\n[ERROR] Gagal mengunduh audio: {error_msg}")
                return False
        else:
            print(f"\n[ERROR] Gagal mengunduh audio: {error_msg}")
            return False

def download_playlist(url, download_path='./downloads'):
    try:
        playlist_info = get_playlist_info(url)
        if playlist_info and playlist_info['videos']:
            # Sanitize playlist title to create a valid folder name
            playlist_title = ''.join(c for c in playlist_info['title'] if c.isalnum() or c in (' ', '-', '_')).strip()
            if not playlist_title:
                playlist_title = 'playlist'
                
            # Create playlist folder
            playlist_path = os.path.join(download_path, playlist_title)
            os.makedirs(playlist_path, exist_ok=True)
            
            # Add videos to queue silently
            for video in playlist_info['videos']:
                download_queue.put({
                    'type': 'video',
                    'url': f"https://www.youtube.com/watch?v={video['url']}",
                    'path': playlist_path,
                    'title': video['title']
                })
            
            # Show info only once
            print(f"\n[INFO] {len(playlist_info['videos'])} video telah ditambahkan ke antrian")
            print("[INFO] Gunakan pilihan '4' untuk melihat status download")
            return True
        else:
            print("\n[ERROR] Tidak dapat mendapatkan informasi playlist atau playlist kosong")
            return False
    except Exception as e:
        error_msg = str(e).split('\n')[0]
        print(f"\n[ERROR] Gagal memproses playlist: {error_msg}")
        return False

def process_queue():
    global program_running
    while program_running:
        try:
            if not download_queue.empty():
                update_activity()  # Update aktivitas saat memulai download
                item = download_queue.get()
                current_download["type"] = item["type"]
                current_download["title"] = item["title"]
                current_download["path"] = item["path"]
                current_download["progress"] = 0
                current_download["total_bytes"] = 0
                current_download["downloaded_bytes"] = 0
                current_download["speed"] = 0
                current_download["eta"] = 0
                
                try:
                    if item["type"] == "video":
                        success = download_video(item["url"], item.get('path', './downloads'), title=item["title"])
                    elif item["type"] == "audio":
                        success = download_audio(item["url"], item.get('path', './downloads'), format=item.get('format', 'mp3'), title=item["title"])
                    
                    if success:
                        print(f"\n[INFO] {item['type'].upper()} '{item['title']}' berhasil diunduh.")
                except Exception as e:
                    error_msg = str(e).split('\n')[0]
                    print(f"\n[ERROR] Gagal mengunduh {item['type']} '{item['title']}': {error_msg}")
                
                current_download["type"] = None
                current_download["title"] = None
                current_download["path"] = None
                current_download["progress"] = 0
                current_download["total_bytes"] = 0
                current_download["downloaded_bytes"] = 0
                current_download["speed"] = 0
                current_download["eta"] = 0
                download_queue.task_done()
            else:
                time.sleep(1.0)
        except Exception as e:
            print(f"Error in process_queue: {e}")
            time.sleep(1.0)

def show_status():
    try:
        while True:
            # Clear screen before showing status
            os.system('cls' if os.name == 'nt' else 'clear')
            
            # Menampilkan antrian
            queue_items = list(download_queue.queue)
            total_items = len(queue_items) + (1 if current_download["type"] is not None else 0)
            
            print("\n=== STATUS DOWNLOAD ===")
            print(f"Total item: {total_items}")
            
            # Tampilkan download aktif dengan progress bar
            if current_download["type"] is not None:
                print(f"\n[DOWNLOAD AKTIF - {current_download['type'].upper()}]")
                print(f"Judul    : {current_download['title']}")
                print(f"Folder   : {os.path.basename(current_download['path'])}")
                
                # Format ukuran dan kecepatan
                total_mb = current_download['total_bytes'] / (1024 * 1024) if current_download['total_bytes'] > 0 else 0
                downloaded_mb = current_download['downloaded_bytes'] / (1024 * 1024) if current_download['downloaded_bytes'] > 0 else 0
                speed_mb = current_download['speed'] / (1024 * 1024) if current_download['speed'] else 0
                
                # Progress bar
                progress = current_download['progress']
                bar_length = 30
                filled_length = int(bar_length * progress / 100)
                bar = '=' * filled_length + '-' * (bar_length - filled_length)
                
                print(f"Progress : [{bar}] {progress:.1f}%")
                
                # Show size info if available
                if total_mb > 0:
                    print(f"Ukuran   : {downloaded_mb:.1f}MB / {total_mb:.1f}MB")
                elif downloaded_mb > 0:
                    print(f"Ukuran   : {downloaded_mb:.1f}MB / ???")
                
                # Show speed if available
                if speed_mb > 0:
                    print(f"Speed    : {speed_mb:.1f}MB/s")
                elif current_download['speed']:
                    print(f"Speed    : {current_download['speed']}")
                
                # Show ETA if available
                if current_download['eta']:
                    if isinstance(current_download['eta'], (int, float)):
                        minutes = int(current_download['eta']) // 60
                        seconds = int(current_download['eta']) % 60
                        print(f"ETA      : {minutes}m {seconds}s")
                    else:
                        print(f"ETA      : {current_download['eta']}")

            # Tampilkan antrian dengan informasi detail
            if queue_items:
                print("\n[ANTRIAN DOWNLOAD]")
                for i, item in enumerate(queue_items, 1):
                    print(f"\n{i}. {item['type'].upper()}")
                    print(f"   Judul  : {item['title']}")
                    print(f"   Folder : {os.path.basename(item['path'])}")
            else:
                print("\n[ANTRIAN DOWNLOAD]")
                print("Tidak ada item dalam antrian")
            
            print("\nPilihan:")
            print("1. Refresh status")
            print("2. Kembali ke menu utama")
            
            choice = input("\nMasukkan pilihan (1-2): ").strip()
            if choice == '2':
                break
            elif choice != '1':
                print("\n[ERROR] Pilihan tidak valid!")
                time.sleep(0.5)
            
            # Jika pilihan 1 atau tidak valid, akan loop dan refresh status
            time.sleep(0.5)  # Delay sebentar sebelum refresh
            
    except Exception as e:
        print(f"\n[ERROR] Gagal menampilkan status: {str(e)}")
        time.sleep(1)

def get_default_download_path():
    if os.path.exists('/data/data/com.termux/files/home/storage/downloads'):
        return '/data/data/com.termux/files/home/storage/downloads/youtube_downloads'
    return './downloads'

def handle_input():
    global program_running
    
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def show_return_message():
        print("\n[INFO] Kembali ke menu utama dalam:")
        for i in range(5, 0, -1):
            print(f"{i}...", end="\r")
            time.sleep(1)
    
    while program_running:
        try:
            clear_screen()
            print("\nYouTube Video/Audio Downloader")
            print("==============================")
            print(f"Program akan berhenti otomatis setelah {IDLE_TIMEOUT//60} menit tidak aktif")
            
            print("\nPilihan:")
            print("1. Download video")
            print("2. Download audio")
            print("3. Download playlist")
            print("4. Tampilkan antrian download")
            print("5. Keluar")
            
            try:
                update_activity()  # Update aktivitas saat menunggu input
                while True:
                    choice = input("\nMasukkan pilihan (1-5): ").strip()
                    if not choice:
                        print("\n[ERROR] Pilihan tidak boleh kosong!")
                        time.sleep(0.5)
                        continue
                    if not choice.isdigit():
                        print("\n[ERROR] Pilihan harus berupa angka!")
                        time.sleep(0.5)
                        continue
                    choice = int(choice)
                    if choice < 1 or choice > 5:
                        print("\n[ERROR] Pilihan harus antara 1-5!")
                        time.sleep(0.5)
                        continue
                    choice = str(choice)  # Convert back to string for compatibility
                    break
                
                if choice == '4':
                    show_status()
                    continue
                    
                if choice == '5':
                    if not download_queue.empty() or current_download["type"] is not None:
                        while True:
                            print("\nMasih ada download yang berjalan atau dalam antrian.")
                            print("Pilihan:")
                            print("1. Tunggu sampai download selesai")
                            print("2. Hentikan semua download dan keluar")
                            
                            while True:
                                exit_choice = input("\nMasukkan pilihan (1-2): ").strip()
                                if not exit_choice:
                                    print("\n[ERROR] Pilihan tidak boleh kosong!")
                                    time.sleep(0.5)
                                    continue
                                if not exit_choice.isdigit():
                                    print("\n[ERROR] Pilihan harus berupa angka!")
                                    time.sleep(0.5)
                                    continue
                                exit_choice = int(exit_choice)
                                if exit_choice < 1 or exit_choice > 2:
                                    print("\n[ERROR] Pilihan harus antara 1-2!")
                                    time.sleep(0.5)
                                    continue
                                exit_choice = str(exit_choice)  # Convert back to string for compatibility
                                break
                            
                            if exit_choice == '1':
                                print("\n[INFO] Menunggu download selesai sebelum menutup program...")
                                print("[INFO] Program akan keluar setelah semua download selesai.")
                                download_queue.join()
                                print("[INFO] Semua download selesai.")
                                print("[INFO] Menutup program...")
                                program_running = False
                                os._exit(0)
                            elif exit_choice == '2':
                                print("\n[INFO] Menghentikan semua download...")
                                while not download_queue.empty():
                                    try:
                                        download_queue.get_nowait()
                                        download_queue.task_done()
                                    except queue.Empty:
                                        break
                                print("[INFO] Menutup program...")
                                program_running = False
                                os._exit(0)
                            else:
                                print("\n[ERROR] Pilihan tidak valid!")
                                time.sleep(0.5)
                    else:
                        print("\n[INFO] Menutup program...")
                        program_running = False
                        os._exit(0)
                
                url = input("\nMasukkan URL YouTube: ").strip()
                if not url:
                    print("\n[ERROR] URL tidak boleh kosong!")
                    time.sleep(0.5)
                    continue
                    
                default_path = get_default_download_path()
                print(f"\nDefault download path: {default_path}")
                download_path = input(f"Masukkan path download (tekan Enter untuk default '{default_path}'): ").strip() or default_path
                
                os.makedirs(download_path, exist_ok=True)
                
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
                        print("[INFO] Gunakan pilihan '4' untuk melihat status download")
                        show_return_message()
                
                elif choice == '2':
                    title = get_video_title(url)
                    if title:
                        download_queue.put({
                            'type': 'audio',
                            'url': url,
                            'path': download_path,
                            'title': title
                        })
                        print(f"\n[INFO] Audio '{title}' ditambahkan ke antrian")
                        print("[INFO] Gunakan pilihan '4' untuk melihat status download")
                        show_return_message()
                
                elif choice == '3':
                    download_playlist(url, download_path)
                    print("[INFO] Gunakan pilihan '4' untuk melihat status download")
                    show_return_message()
                
                else:
                    print("\n[ERROR] Pilihan tidak valid!")
                    
            except Exception as e:
                error_msg = str(e).split('\n')[0]
                print(f"\n[ERROR] Terjadi kesalahan: {error_msg}")
                
            time.sleep(0.5)
                
        except KeyboardInterrupt:
            print("\n\n[INFO] Program dihentikan oleh pengguna...")
            program_running = False
            os._exit(0)
        except Exception as e:
            print(f"\n[ERROR] Terjadi kesalahan yang tidak diharapkan: {e}")
            time.sleep(1.0)

def main():
    global program_running
    # Jalankan thread untuk memproses antrian download
    threading.Thread(target=process_queue, daemon=True).start()
    # Jalankan thread untuk mengecek timeout
    threading.Thread(target=check_idle_timeout, daemon=True).start()
    # Jalankan thread untuk input pengguna
    threading.Thread(target=handle_input, daemon=False).start()

if __name__ == "__main__":
    main()
