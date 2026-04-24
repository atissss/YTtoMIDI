from pathlib import Path

import numpy as np
from pydub import AudioSegment

SUPPORTED_EXTENSIONS = ['*.wav', '*.mp3', '*.flac', '*.ogg', '*.m4a', '*.aac']


def get_processed_folder() -> Path:
    return Path(__file__).resolve().parents[2] / 'data' / 'downloads' / 'processed'


def find_processed_audio_files(processed_folder: Path | None = None) -> list[Path]:
    processed_folder = Path(processed_folder) if processed_folder is not None else get_processed_folder()
    if not processed_folder.exists():
        return []

    files: list[Path] = []
    for pattern in SUPPORTED_EXTENSIONS:
        files.extend(sorted(processed_folder.glob(pattern)))
    return files


def choose_audio_file(files: list[Path]) -> Path:
    if not files:
        raise FileNotFoundError('No processed audio files found in the processed folder.')

    for index, audio_file in enumerate(files, start=1):
        print(f'  {index}: {audio_file.name}')

    choice = input('Enter file number to detect pitches from (press Enter for the latest file): ').strip()
    if not choice:
        return files[-1]

    try:
        selected_index = int(choice) - 1
        return files[selected_index]
    except (ValueError, IndexError):
        raise ValueError('Invalid selection.')


def load_audio(audio_path: Path | str) -> tuple[np.ndarray, int]:
    audio = AudioSegment.from_file(str(audio_path))
    audio = audio.set_channels(1)
    sample_rate = audio.frame_rate
    samples = np.asarray(audio.get_array_of_samples(), dtype=np.float32)
    max_val = float(2 ** (8 * audio.sample_width - 1))
    samples = samples / max_val
    return samples, sample_rate


def detect_pitch_autocorrelation(
    frame: np.ndarray,
    sample_rate: int,
    fmin: float = 80.0,
    fmax: float = 1200.0,
    threshold: float = 0.3,
) -> float | None:
    frame = frame - np.mean(frame)
    if not np.any(frame):
        return None

    window = np.hanning(len(frame))
    frame = frame * window

    correlation = np.correlate(frame, frame, mode='full')
    correlation = correlation[len(correlation) // 2 :]
    if correlation.size == 0:
        return None

    correlation = correlation / np.max(np.abs(correlation))
    lag_min = max(1, int(sample_rate / fmax))
    lag_max = min(int(sample_rate / fmin), correlation.size - 1)
    if lag_min >= lag_max:
        return None

    best_lag = np.argmax(correlation[lag_min : lag_max + 1]) + lag_min
    confidence = correlation[best_lag]
    if confidence < threshold:
        return None

    return sample_rate / best_lag


def detect_pitches(
    audio_path: Path | str,
    frame_length: int = 4096,
    hop_length: int = 1024,
    fmin: float = 80.0,
    fmax: float = 1200.0,
    threshold: float = 0.3,
) -> list[tuple[float, float]]:
    signal, sample_rate = load_audio(audio_path)
    if signal.size < frame_length:
        padding = frame_length - signal.size
        signal = np.pad(signal, (0, padding), mode='constant')

    pitches: list[tuple[float, float]] = []
    for start in range(0, len(signal) - frame_length + 1, hop_length):
        frame = signal[start : start + frame_length]
        frequency = detect_pitch_autocorrelation(frame, sample_rate, fmin=fmin, fmax=fmax, threshold=threshold)
        if frequency is not None:
            time_seconds = start / sample_rate
            pitches.append((time_seconds, frequency))

    return pitches


if __name__ == '__main__':
    processed_folder = get_processed_folder()
    audio_files = find_processed_audio_files(processed_folder)

    if not audio_files:
        print(f'No processed audio files found in {processed_folder}')
        raise SystemExit(1)

    print('Processed audio files:')
    try:
        selected_audio = choose_audio_file(audio_files)
    except ValueError as error:
        print(error)
        raise SystemExit(1)

    pitch_list = detect_pitches(selected_audio)
    if not pitch_list:
        print('No pitches detected.')
        raise SystemExit(0)

    print('Detected pitches (time, frequency):')
    for time_seconds, frequency in pitch_list:
        print(f'{time_seconds:.3f}s -> {frequency:.2f} Hz')
