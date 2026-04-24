from pathlib import Path
import sys

import numpy as np
import pretty_midi

# Add project root to path for imports
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

MIDI_FOLDER = Path(__file__).resolve().parents[2] / 'data' / 'midi'


from src.pitch.pitch_detection import detect_pitches, find_processed_audio_files

def get_midi_folder() -> Path:
    MIDI_FOLDER.mkdir(parents=True, exist_ok=True)
    return MIDI_FOLDER

def frequency_to_midi_number(frequency: float) -> int | None:
    if frequency <= 0:
        return None
    note_number = 69 + 12 * np.log2(frequency / 440.0)
    midi_note = int(round(note_number))
    if midi_note < 0 or midi_note > 127:
        return None
    return midi_note


def merge_pitch_segments(
    pitch_list: list[tuple[float, float]],
    max_gap: float = 0.05,
    min_duration: float = 0.05,
) -> list[tuple[int, float, float]]:
    segments: list[tuple[int, float, float]] = []
    current_note: int | None = None
    segment_start: float | None = None
    last_time: float | None = None

    for time_seconds, frequency in pitch_list:
        note = frequency_to_midi_number(frequency)
        if note is None:
            continue

        if current_note is None:
            current_note = note
            segment_start = time_seconds
            last_time = time_seconds
            continue

        if note == current_note and last_time is not None and time_seconds - last_time <= max_gap:
            last_time = time_seconds
            continue

        if current_note is not None and segment_start is not None and last_time is not None:
            duration = max(last_time - segment_start + min_duration, min_duration)
            segments.append((current_note, segment_start, segment_start + duration))

        current_note = note
        segment_start = time_seconds
        last_time = time_seconds

    if current_note is not None and segment_start is not None and last_time is not None:
        duration = max(last_time - segment_start + min_duration, min_duration)
        segments.append((current_note, segment_start, segment_start + duration))

    return segments


def convert_pitch_list_to_midi(
    pitch_list: list[tuple[float, float]],
    output_path: Path | str | None = None,
    program: int = 0,
    velocity: int = 100,
) -> Path:
    if not pitch_list:
        raise ValueError('Pitch list must contain at least one time/frequency pair.')

    midi_folder = get_midi_folder()
    if output_path is None:
        output_path = midi_folder / 'output.mid'
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pretty_midi_obj = pretty_midi.PrettyMIDI()
    instrument = pretty_midi.Instrument(program=program)

    segments = merge_pitch_segments(pitch_list)
    for note_number, start_time, end_time in segments:
        note = pretty_midi.Note(velocity=velocity, pitch=note_number, start=start_time, end=end_time)
        instrument.notes.append(note)

    pretty_midi_obj.instruments.append(instrument)
    pretty_midi_obj.write(str(output_path))
    return output_path


def save_pitch_list_as_midi(
    pitch_list: list[tuple[float, float]],
    filename: str = 'converted.mid',
    program: int = 0,
    velocity: int = 100,
) -> Path:
    midi_folder = get_midi_folder()
    output_path = midi_folder / filename
    return convert_pitch_list_to_midi(pitch_list, output_path=output_path, program=program, velocity=velocity)


if __name__ == '__main__':
    print('Converting the latest processed audio to MIDI...')
    processed_files = find_processed_audio_files()
    if not processed_files:
        print('No processed audio files found.')
        raise SystemExit(1)

    latest_audio = processed_files[-1]
    print(f'Using: {latest_audio}')
    pitch_list = detect_pitches(latest_audio)
    if not pitch_list:
        print('No pitches detected in the audio.')
        raise SystemExit(1)

    midi_path = save_pitch_list_as_midi(pitch_list, filename='output.mid')
    print(f'MIDI saved to: {midi_path}')
