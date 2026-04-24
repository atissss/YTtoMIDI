from pathlib import Path

from pydub import AudioSegment, silence


AUDIO_EXTENSIONS = ['*.wav', '*.mp3', '*.flac', '*.ogg', '*.m4a', '*.aac', '*.wma']


def get_downloads_folder() -> Path:
    return Path(__file__).resolve().parents[2] / 'data' / 'downloads'


def find_audio_files(downloads_folder: Path | None = None) -> list[Path]:
    downloads_folder = Path(downloads_folder) if downloads_folder is not None else get_downloads_folder()
    if not downloads_folder.exists():
        return []

    files: list[Path] = []
    for pattern in AUDIO_EXTENSIONS:
        files.extend(sorted(downloads_folder.glob(pattern)))
    return files


def load_audio(audio_path: Path | str) -> AudioSegment:
    audio_path = Path(audio_path)
    return AudioSegment.from_file(str(audio_path))


def normalize_audio_segment(audio: AudioSegment, target_dBFS: float = -20.0) -> AudioSegment:
    change_in_dBFS = target_dBFS - audio.dBFS
    return audio.apply_gain(change_in_dBFS)


def trim_silence(audio: AudioSegment, min_silence_len: int = 500, silence_thresh: int = -40) -> AudioSegment:
    nonsilent_ranges = silence.detect_nonsilent(audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh)
    if not nonsilent_ranges:
        return audio

    start = nonsilent_ranges[0][0]
    end = nonsilent_ranges[-1][1]
    return audio[start:end]


def get_default_output_path(audio_file: Path, audio_format: str = 'wav') -> Path:
    processed_folder = audio_file.parent / 'processed'
    processed_folder.mkdir(parents=True, exist_ok=True)
    return processed_folder / f'{audio_file.stem}_cleaned.{audio_format}'


def clean_audio_file(
    audio_path: Path | str,
    output_path: Path | str | None = None,
    audio_format: str = 'wav',
    sample_rate: int = 44100,
    target_dBFS: float = -20.0,
    silence_thresh: int = -40,
    min_silence_len: int = 500,
    high_pass_freq: int = 80,
) -> Path:
    audio_path = Path(audio_path)
    if output_path is None:
        output_path = get_default_output_path(audio_path, audio_format)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    audio = load_audio(audio_path)
    audio = audio.set_channels(1).set_frame_rate(sample_rate)
    audio = audio.high_pass_filter(high_pass_freq)
    audio = trim_silence(audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh)
    audio = normalize_audio_segment(audio, target_dBFS=target_dBFS)

    audio.export(str(output_path), format=audio_format)
    return output_path


def choose_audio_file(files: list[Path]) -> Path:
    if not files:
        raise FileNotFoundError('No audio files found in the downloads folder.')

    for index, audio_file in enumerate(files, start=1):
        print(f'  {index}: {audio_file.name}')

    choice = input('Enter file number to preprocess (press Enter for the latest file): ').strip()
    if not choice:
        return files[-1]

    try:
        selected_index = int(choice) - 1
        return files[selected_index]
    except (ValueError, IndexError):
        raise ValueError('Invalid selection.')


if __name__ == '__main__':
    downloads_folder = get_downloads_folder()
    audio_files = find_audio_files(downloads_folder)

    if not audio_files:
        print(f'No audio files found in {downloads_folder}')
        raise SystemExit(1)

    print('Audio files in downloads:')
    selected_audio = None
    try:
        selected_audio = choose_audio_file(audio_files)
    except ValueError as error:
        print(error)
        raise SystemExit(1)

    output_format = input('Enter output audio format [wav]: ').strip() or 'wav'
    output_path = get_default_output_path(selected_audio, output_format)

    try:
        result_path = clean_audio_file(
            selected_audio,
            output_path=output_path,
            audio_format=output_format,
        )
        print(f'Cleaned audio exported to: {result_path}')
    except Exception as error:
        print('Failed to preprocess the audio file.')
        print(error)
        raise SystemExit(1)
