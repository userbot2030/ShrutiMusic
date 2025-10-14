import subprocess

def enhance_audio(input_audio_path, output_audio_path):
    """
    Menjernihkan audio menggunakan ffmpeg.
    """
    cmd = [
        'ffmpeg', '-y', '-i', input_audio_path,
        '-af', 'afftdn,loudnorm',
        '-c:a', 'libmp3lame', '-q:a', '2',
        output_audio_path
    ]
    try:
        subprocess.run(cmd, check=True)
    except Exception as e:
        print(f"Enhance audio error: {e}")

def enhance_video(input_video_path, output_video_path):
    """
    Membuat video HD menggunakan ffmpeg.
    """
    cmd = [
        'ffmpeg', '-y', '-i', input_video_path,
        '-vf', 'scale=1280:720',
        '-b:v', '2500k', '-c:a', 'aac', '-b:a', '192k',
        output_video_path
    ]
    try:
        subprocess.run(cmd, check=True)
    except Exception as e:
        print(f"Enhance video error: {e}")
