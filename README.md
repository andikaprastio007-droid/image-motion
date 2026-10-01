# IMAGE → MOTION STOCK STUDIO
Gambar → analisis → 10 prompt motion → preview video (FFmpeg mock) → metadata stock. Jalan di Android/Termux.

## Instalasi (Termux)
```
pkg update && pkg install -y git python python-pillow ffmpeg
cd image-motion-studio && ./install.sh
```
Jika pip gagal memasang Pillow, pastikan `python-pillow` dari pkg sudah terpasang.

## Konfigurasi
Edit `.env` (salinan `.env.example`):
- `AI_PROVIDER=anthropic` atau `openai`, `AI_API_KEY=...` untuk analisis gambar AI. Kosong = fallback lokal.
- `VIDEO_PROVIDER` / `VIDEO_API_KEY`: slot untuk API image-to-video. Isi adapter di `backend/providers/video_provider.py`. Kosong = mock FFmpeg.
- `HOST=0.0.0.0` agar bisa diakses dari perangkat lain. `DEBUG=true` untuk stack trace di terminal.

## Menjalankan
`./start.sh` (atau `python app.py`) lalu buka http://127.0.0.1:3000

## Cara pakai
Create → upload gambar → ⚡ Analisis + Generate Dewa → lihat 10 prompt di Lab (edit/copy/favorit) → 🎬 Preview → ⬇ Export MP4.

## Catatan jujur
- Preview video adalah efek zoom/pan FFmpeg, **bukan** AI video generation.
- Tanpa AI vision, analisis lokal hanya membaca warna/tone/rasio. Deteksi teks/logo/wajah butuh AI provider; tanpa itu ditandai "unchecked".
- Output 4K belum didukung (hanya 1080p).

## Test
```
curl http://127.0.0.1:3000/api/health
curl -F image=@foto.jpg http://127.0.0.1:3000/api/upload
```
