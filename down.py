import os
import yt_dlp

def download_video(url, download_path='./downloads'):
    os.makedirs(download_path, exist_ok=True)

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',  # Download video dan audio terbaik
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',  # Convert output to mp4
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            print("Video dan audio berhasil diunduh.")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

def download_audio(url, download_path='./downloads', format='mp3'):
    os.makedirs(download_path, exist_ok=True)

    # Menentukan opsi untuk format audio
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]',  # Download audio terbaik
        'outtmpl': os.path.join(download_path, f'%(title)s.{format}'),  # Menggunakan format yang ditentukan
    }

    # Jika format tidak ditentukan, gunakan mp3 sebagai default
    if not format or format.lower() != 'mp3':
        format = 'mp3'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            # Ubah nama file hasil download jika menggunakan format mp3
            for file in os.listdir(download_path):
                if file.endswith('.m4a'):
                    new_filename = os.path.splitext(file)[0] + '.' + format
                    os.rename(os.path.join(download_path, file), os.path.join(download_path, new_filename))
            print("Audio berhasil diunduh.")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

def main():
    while True:
        print("\nPilihan:")
        print("1. Download video dan audio")
        print("2. Download audio saja")
        print("3. Exit")
        choice = input("Masukkan pilihan (1, 2 atau 3): ")

        if choice == '1':
            video_url = input("Masukkan URL YouTube: ")
            download_video(video_url)
        elif choice == '2':
            audio_url = input("Masukkan URL YouTube: ")
            download_audio(audio_url)  # Default format 'mp3' digunakan
        elif choice == '3':
            print("Terima kasih telah menggunakan program ini!")
            break
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")

if __name__ == "__main__":
    main()
