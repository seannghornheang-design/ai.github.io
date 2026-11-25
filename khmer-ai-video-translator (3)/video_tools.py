"""Utilities reserved for YouTube URL validation and future speaker diarization."""
from urllib.parse import urlparse

def is_youtube_url(url):
    return urlparse(url).netloc.lower() in {"youtube.com","www.youtube.com","m.youtube.com","youtu.be"}
