import os, tempfile, subprocess, requests, html
from pathlib import Path
from openai import OpenAI
from pydub import AudioSegment

def secret(name):
    try:
        import streamlit as st
        return st.secrets.get(name) or os.getenv(name)
    except Exception:
        return os.getenv(name)

def run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode:
        raise RuntimeError(p.stderr[-3000:])
    return p

def azure_tts(text, voice, out_path):
    key, region = secret("AZURE_SPEECH_KEY"), secret("AZURE_SPEECH_REGION")
    url = "https://" + region + ".tts.speech.microsoft.com/cognitiveservices/v1"
    ssml = '<speak version="1.0" xml:lang="km-KH"><voice name="' + voice + '">' + html.escape(text) + '</voice></speak>'
    r = requests.post(url, headers={
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "riff-24khz-16bit-mono-pcm"
    }, data=ssml.encode("utf-8"), timeout=120)
    r.raise_for_status()
    Path(out_path).write_bytes(r.content)

def translate_text(client, text):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role":"system","content":"Translate this spoken content into natural, clear Khmer. Preserve meaning, names, numbers and tone. Return only the Khmer translation."},
            {"role":"user","content":text}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content.strip()

def srt_time(seconds):
    ms = int(seconds * 1000)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def translate_video(video_bytes, filename, voice, burn_subtitles=True):
    client = OpenAI(api_key=secret("OPENAI_API_KEY"))
    work = Path(tempfile.mkdtemp(prefix="khmer_video_"))
    input_path = work / ("input" + (Path(filename).suffix or ".mp4"))
    audio_path = work / "source.wav"
    input_path.write_bytes(video_bytes)

    run(["ffmpeg", "-y", "-i", str(input_path), "-vn", "-ac", "1", "-ar", "16000", str(audio_path)])
    with open(audio_path, "rb") as audio:
        transcript = client.audio.transcriptions.create(
            model="whisper-1", file=audio, response_format="verbose_json",
            timestamp_granularities=["segment"]
        )

    segments = getattr(transcript, "segments", None) or []
    if not segments:
        raise RuntimeError("មិនអាចរកឃើញផ្នែកសំឡេងដែលមាន timestamp បានទេ។")

    dubbed = AudioSegment.silent(duration=0, frame_rate=24000)
    srt_lines = []
    for idx, seg in enumerate(segments, start=1):
        start, end = float(seg.start), float(seg.end)
        original = seg.text.strip()
        if not original:
            continue
        khmer = translate_text(client, original)
        speech_path = work / f"speech_{idx}.wav"
        azure_tts(khmer, voice, speech_path)
        speech = AudioSegment.from_file(speech_path)
        target_ms = max(250, int((end-start)*1000))
        if len(speech) > target_ms:
            speech = speech.speedup(playback_speed=min(1.8, len(speech)/target_ms))
        # Build a timeline by placing each spoken segment at its original timestamp.
        needed = int(end * 1000)
        if len(dubbed) < needed:
            dubbed += AudioSegment.silent(duration=needed-len(dubbed), frame_rate=24000)
        dubbed = dubbed.overlay(speech, position=int(start*1000))
        srt_lines.append(f"{len(srt_lines)+1}\n{srt_time(start)} --> {srt_time(end)}\n{khmer}\n")

    if len(dubbed) < len(AudioSegment.from_file(audio_path)):\n        dubbed += AudioSegment.silent(duration=len(AudioSegment.from_file(audio_path))-len(dubbed), frame_rate=24000)\n\n    dubbed_path = work / "khmer_voice.wav"
    dubbed.export(dubbed_path, format="wav")
    srt_path = work / "khmer_subtitles.srt"
    srt_path.write_text("\n".join(srt_lines), encoding="utf-8")
    output_path = work / "khmer_translated.mp4"

    if burn_subtitles:
        escaped = str(srt_path).replace("\\\\", "/").replace(":", "\\\\:")
        run(["ffmpeg", "-y", "-i", str(input_path), "-i", str(dubbed_path),
             "-vf", f"subtitles={escaped}:force_style='FontName=Noto Sans Khmer,FontSize=22,Outline=1'",
             "-map", "0:v:0", "-map", "1:a:0", "-c:v", "libx264", "-preset", "veryfast",
             "-c:a", "aac", "-shortest", str(output_path)])
    else:
        run(["ffmpeg", "-y", "-i", str(input_path), "-i", str(dubbed_path),
             "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac",
             "-shortest", str(output_path)])
    return {"video_path": str(output_path), "srt_path": str(srt_path)}
