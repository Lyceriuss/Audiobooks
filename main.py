import os
import urllib.parse
import xml.etree.ElementTree as ET
from email.utils import formatdate
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles

# Directory on your computer/container where audiobook files live
AUDIO_DIR = os.getenv("AUDIO_DIR", "/app/audiobooks")

app = FastAPI()

# Built-in static file server handles HTTP 206 range requests for iOS automatically
app.mount("/files", StaticFiles(directory=AUDIO_DIR, check_dir=False), name="files")

@app.get("/feed.xml")
def get_podcast_feed(request: Request):
    base_url = str(request.base_url).rstrip("/").replace("http://", "https://")
    
    # 1. Build RSS 2.0 structure with iTunes XML namespaces
    rss = ET.Element("rss", {
        "version": "2.0",
        "xmlns:itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
        "xmlns:content": "http://purl.org/rss/1.0/modules/content/"
    })
    
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "Personal Audiobook Library"
    ET.SubElement(channel, "link").text = base_url
    ET.SubElement(channel, "language").text = "en-us"
    ET.SubElement(channel, "itunes:author").text = "Audiobook Server"
    ET.SubElement(channel, "itunes:type").text = "serial"  # Signals long-form/series content
    ET.SubElement(channel, "description").text = "Self-hosted private audiobook feed."

    # 2. Iterate audio files in the folder
    valid_exts = (".m4b", ".mp3", ".m4a", ".aac", ".ogg")
    if os.path.exists(AUDIO_DIR):
        files = sorted([f for f in os.listdir(AUDIO_DIR) if f.lower().endswith(valid_exts)])
    else:
        files = []

    for filename in files:
        filepath = os.path.join(AUDIO_DIR, filename)
        file_size = os.path.getsize(filepath)
        mod_time = os.path.getmtime(filepath)
        
        ext = os.path.splitext(filename)[1].lower()
        mime_type = "audio/mp4" if ext in (".m4b", ".m4a", ".aac") else "audio/mpeg"
        
        encoded_name = urllib.parse.quote(filename)
        audio_url = f"{base_url}/files/{encoded_name}"
        
        title = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ")

        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = title
        ET.SubElement(item, "guid", {"isPermaLink": "false"}).text = filename
        ET.SubElement(item, "pubDate").text = formatdate(mod_time, usegmt=True)
        ET.SubElement(item, "enclosure", {
            "url": audio_url,
            "length": str(file_size),
            "type": mime_type
        })

    xml_bytes = ET.tostring(rss, encoding="utf-8", xml_declaration=True)
    return Response(content=xml_bytes, media_type="application/rss+xml")