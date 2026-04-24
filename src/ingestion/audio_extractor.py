import subprocess
from pathlib import Path

def get_downloads_folder() -> Path:
    return Path(__file__).resolve().parents[2] / 'data' / 'downloads'

def find_video_files(downloads_folder: Path | None = None) -> list[Path]:
    downloads_folder = Path(downloads_folder) if downloads_folder is not None else get_downloads_folder()
    if not downloads_folder.exists():
        return []

    extensions = ['*.mp4', '*.mkv', '*.webm', '*.mov', '*.avi', '*.flv', '*.mpg', '*.mpeg', '*.m4v']
    files: list[Path] = []
    for pattern in extensions:
        files.extend(sorted(downloads_folder.glob(pattern)))
    return files

def get_default_output_path(video_file: Path, audio_format: str = 'mp3') -> Path:
    return video_file.with_suffix(f'.{audio_format}')

def extract_audio_from_video(
    video_path: Path | str,
    output_path: Path | str | None = None,
    audio_format: str = 'mp3',
    ffmpeg_path: str = 'ffmpeg',
) -> Path:
    video_path = Path(video_path)
    if output_path is None:
        output_path = get_default_output_path(video_path, audio_format)
    output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if audio_format.lower() == 'mp3':
        audio_args = ['-c:a', 'libmp3lame', '-q:a', '2']
    elif audio_format.lower() == 'wav':
        audio_args = ['-c:a', 'pcm_s16le']
    else:
        audio_args = ['-c:a', 'copy']

    command = [
        ffmpeg_path,
        '-y',
        '-i', str(video_path),
        '-vn',
        *audio_args,
        str(output_path),
    ]

    subprocess.run(command, check=True)
    return output_path

def extract_audio_from_latest_video(audio_format: str = 'mp3') -> Path:
    videos = find_video_files()
    if not videos:
        raise FileNotFoundError('No downloaded video files found in data/downloads.')

    return extract_audio_from_video(videos[-1], audio_format=audio_format)

if __name__ == '__main__':
    downloads_folder = get_downloads_folder()
    videos = find_video_files(downloads_folder)

    if not videos:
        print(f'No video files found in {downloads_folder}')
        raise SystemExit(1)

    print('Downloaded video files:')
    for index, video_file in enumerate(videos, start=1):
        print(f'  {index}: {video_file.name}')

    choice = input('Enter file number to extract audio from (press Enter for the latest file): ').strip()
    if choice:
        try:
            selected_index = int(choice) - 1
            video_path = videos[selected_index]
        except (ValueError, IndexError):
            print('Invalid selection.')
            raise SystemExit(1)
    else:
        video_path = videos[-1]

    output_format = input('Enter output audio format [mp3]: ').strip() or 'mp3'
    output_file = get_default_output_path(video_path, output_format)

    try:
        result_path = extract_audio_from_video(video_path, output_file, audio_format=output_format)
        print(f'Audio extracted to {result_path}')
    except subprocess.CalledProcessError as error:
        print('FFmpeg failed to extract audio. Make sure FFmpeg is installed and available on PATH.')
        print(error)
        raise SystemExit(1)
