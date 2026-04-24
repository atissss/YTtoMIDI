Generated file structure in ChatGPT
Final outcome may differ from this

YES THIS IS VIBE CODED.

```
choir-midi-transcriber/
│
├── src/
│   ├── core/
│   │   ├── pipeline.py
│   │   ├── config.py
│   │   └── utils.py
│   │
│   ├── ingestion/
│   │   ├── youtube_downloader.py
│   │   └── audio_extractor.py
│   │
│   ├── preprocessing/
│   │   ├── audio_cleaning.py
│   │   └── normalization.py
│   │
│   ├── separation/
│   │   ├── demucs_wrapper.py
│   │   └── stem_manager.py
│   │
│   ├── pitch/
│   │   ├── pitch_detection.py
│   │   ├── multi_pitch.py
│   │   └── frequency_processing.py
│   │
│   ├── midi/
│   │   ├── midi_converter.py
│   │   └── note_quantizer.py
│   │
│   ├── classification/
│   │   ├── voice_classifier.py
│   │   └── satb_rules.py
│   │
│   ├── evaluation/
│   │   ├── metrics.py
│   │   └── compare_midi.py
│   │
│   └── interface/
│       ├── cli.py
│       └── app.py   # (Streamlit later)
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── stems/
│   └── midi/
│
├── models/
│   ├── pretrained/
│   └── finetuned/
│
├── notebooks/
│   ├── experiments.ipynb
│   └── pitch_analysis.ipynb
│
├── tests/
│   ├── test_pitch.py
│   ├── test_midi.py
│   └── test_pipeline.py
│
├── configs/
│   ├── default.yaml
│   └── dev.yaml
│
├── scripts/
│   ├── run_pipeline.py
│   └── download_sample.py
│
├── requirements.txt
├── README.md
└── .gitignore
