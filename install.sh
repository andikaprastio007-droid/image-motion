#!/data/data/com.termux/files/usr/bin/bash
set -e
pkg update -y
pkg install -y python python-pillow ffmpeg
pip install flask python-dotenv
[ -f .env ] || cp .env.example .env
mkdir -p projects outputs uploads logs
echo "Selesai. Jalankan: ./start.sh"
