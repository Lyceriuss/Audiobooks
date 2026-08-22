# Audiobook Streamer

A simple way to share audiobooks (`.m4b`, `.mp3`) from a laptop folder with someone's phone using podcast apps like Apple Podcasts, Pocket Casts, or AntennaPod.

Instead of building a custom mobile app, this spins up an RSS feed from your local files. The podcast app on their phone handles all the heavy lifting: downloading for offline listening, remembering where they stopped, and lock-screen controls.

Simply get this link: `https://your-tunnel-url.trycloudflare.com` from logs audiobook-tunnel and add `/feed.xml` to it. So it looks like this: `https://your-tunnel-url.trycloudflare.com/feed.xml`

* **iPhone (Apple Podcasts):** Open app $\to$ Library $\to$ tap ... (top right) $\to$ Follow a Show by URL... $\to$ Paste link $\to$ Follow.
* **Android (AntennaPod):** Tap + (Add Podcast) $\to$ Add Podcast by RSS address $\to$ Paste link $\to$ Subscribe.
* **Android (Pocket Casts):** Paste link into the Discover / Search bar $\to$ Tap search $\to$ Subscribe.
* **Android (YouTube Music):** Library $\to$ Podcasts $\to$ Add Podcast $\to$ Add a podcast by RSS feed $\to$ Paste link $\to$ Add.

---

## The Quick Stats

* **Cost:** **$0** (Runs locally on your machine + free Cloudflare Quick Tunnel).
* **Laptop Resource Usage:** Extremely low (~70 MB RAM total, <1% idle CPU). It just serves files directly without re-encoding audio.
* **Requirements:** Docker & Docker Compose.
* **Compatibility:** 
  *  **Works with:** Apple Podcasts, Pocket Casts, AntennaPod, Overcast, YouTube Music (RSS).
  * ❌ **Does NOT work with:** Spotify (Spotify does not allow adding private RSS feeds via URL).

---

## How It Works

1. **`main.py` (FastAPI):** Scans the `./books` folder, generates an Apple-compatible `feed.xml`, and streams audio using byte ranges so scrubbing works instantly.
2. **Cloudflare Tunnel:** Creates a secure, temporary HTTPS link so the feed works outside your home Wi-Fi (over mobile data) without messing with router settings or port forwarding.
3. **Podcast App:** Handles streaming, downloads, CarPlay/Android Auto, and keeps track of timestamps locally on the listener's device.

---

## Quick Setup

### 1. Add your audiobooks
Create a `books/` folder in the project directory and move your `.m4b`, `.mp3`, or `.m4a` files into it:

```bash
mkdir -p books
cp /path/to/your/audiobooks/*.m4b books/

docker compose up -d --build

docker logs audiobook-tunnel 2>&1 | grep -o 'https://.*\.trycloudflare\.com'