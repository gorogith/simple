import os
import yt_dlp

def format_bytes(size):
    if size is None:
        return "unknown size"
    for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0

def download_video(video_url, download_path='./downloads'):
    os.makedirs(download_path, exist_ok=True)
    
    # Konfigurasi yt-dlp untuk mengunduh video dengan resolusi terbaik
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            video_title = info_dict.get('title', None)
            print(f"\nVideo '{video_title}' telah berhasil diunduh di {download_path}")
    except yt_dlp.utils.DownloadError as e:
        print(f"Error downloading video: {e}")

def download_videos_from_channel(channel_url, download_path='./downloads'):
    os.makedirs(download_path, exist_ok=True)

    try:
        with yt_dlp.YoutubeDL() as ydl:
            info_dict = ydl.extract_info(channel_url, download=False)
            channel_title = info_dict.get('title', 'Unknown Channel')

            if not info_dict.get('entries'):
                print("Tidak ada video ditemukan di saluran ini.")
                return

            channel_download_path = os.path.join(download_path, channel_title)
            os.makedirs(channel_download_path, exist_ok=True)

            for entry in info_dict['entries']:
                video_url = entry.get('webpage_url', None)
                if video_url:
                    print(f"\nMengunduh video dari '{entry.get('title', 'No Title')}'")
                    download_video(video_url, channel_download_path)
            
            print(f"\nSemua video di saluran '{channel_title}' telah berhasil diunduh.")
    except yt_dlp.utils.DownloadError as e:
        print(f"Error downloading channel: {e}")

def main():
    while True:
        print("\nPilihan:")
        print("1. Download video dari URL YouTube")
        print("2. Download semua video dari saluran YouTube")
        print("3. Exit")
        choice = input("Masukkan pilihan (1, 2 atau 3): ")

        if choice == '1':
            video_url = input("Masukkan URL YouTube: ")
            download_video(video_url)
        elif choice == '2':
            channel_url = input("Masukkan URL saluran YouTube: ")
            download_videos_from_channel(channel_url)
        elif choice == '3':
            print("Terima kasih telah menggunakan program ini!")
            break
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")

if __name__ == "__main__":
    main()
