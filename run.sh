python3 ./transmission.py
ffmpeg -f s16le -ar 8000  -i data.pcm -ar 8000 out.wav
afplay ./out.wav
