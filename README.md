# YouTube Video & Audio Downloader on python

Aplikasi download video dan audio YouTube dengan fitur antrian dan download playlist. Mendukung penggunaan di Linux dan Termux (Android).

## Fitur Utama

### 1. Download Video
- Kualitas video terbaik (up to 4K)
- Format MP4
- Mendukung subtitle (jika tersedia)

### 2. Download Audio
- Format MP3 atau M4A
- Kualitas audio terbaik
- Otomatis konversi ke format yang dipilih

### 3. Download Playlist
- Download seluruh video dalam playlist
- Membuat folder terpisah untuk setiap playlist
- Melanjutkan download jika terjadi error pada video tertentu

### 4. Sistem Antrian 
- Download di background
- Bisa menambahkan banyak video/playlist ke antrian
- Melihat status download yang sedang berjalan
- Bisa menambahkan download sambil menunggu download lain selesai

## Instalasi di Termux

1. Install Termux dari F-Droid (direkomendasikan) atau Play Store

2. Buka Termux dan jalankan perintah berikut:
```bash
# Izinkan Termux mengakses penyimpanan
termux-setup-storage

# Update dan install paket yang diperlukan
pkg update -y
pkg install -y python ffmpeg python-pip git

# Clone repository (jika menggunakan git)
git clone [URL_REPOSITORY]
cd youtube_video_audio_downloader

# Atau download manual dan extract ke folder

# Install yt-dlp
pip install yt-dlp
```

## Instalasi di Linux

1. Buka terminal dan install dependencies:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip ffmpeg git

# Fedora
sudo dnf install -y python3 python3-pip ffmpeg git

# Arch Linux
sudo pacman -S python python-pip ffmpeg git

# Install yt-dlp
pip3 install yt-dlp
```

2. Download program:
```bash
git clone [URL_REPOSITORY]
cd youtube_video_audio_downloader
```

## Cara Penggunaan

### Menggunakan donwloader.py (Direkomendasikan)
```bash
python downloader.py
```

Menu yang tersedia:
1. Download video - Download single video
2. Download audio - Download audio saja (MP3/M4A)
3. Download playlist - Download seluruh video dalam playlist
4. Tampilkan status - Lihat progress download
5. Keluar - Keluar dari program


## Lokasi Download

### Di Termux
Default: `/data/data/com.termux/files/home/storage/downloads/youtube_downloads`

### Di Linux
Default: `./downloads` (folder 'downloads' di direktori program)

Anda bisa mengubah lokasi download saat program meminta input path.



## Catatan Penting

1. Pastikan koneksi internet stabil
2. Untuk playlist besar, siapkan ruang penyimpanan yang cukup
3. Beberapa video mungkin tidak bisa didownload karena pembatasan dari YouTube
4. Update yt-dlp secara berkala untuk fitur terbaru


## Disclaimer

Program ini hanya untuk keperluan edukasi. Pastikan mematuhi Terms of Service YouTube dan hak cipta yang berlaku.
