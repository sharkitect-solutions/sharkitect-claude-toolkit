---
name: transcribe
description: "Use when transcribing audio/video files to text, speech-to-text from recordings, speaker diarization, labeling speakers in interviews/meetings/podcasts, or extracting text from audio. NEVER for real-time STT/TTS pipelines or voice agent implementation (use voice-ai-development). NEVER for voice agent architecture or multi-agent voice systems (use voice-agents). NEVER for audio editing, mixing, or processing (use standard audio tools). NEVER for phone system configuration or IVR (use twilio-communications)."
---

# Audio Transcribe

Transcribe audio using OpenAI's transcription API via the bundled CLI. Supports plain text, structured JSON, and speaker-diarized output with optional known-speaker identification.

## File Index

| File | Purpose |
|------|---------|
| `scripts/transcribe_diarize.py` | Python CLI (277 lines) - transcription with diarization, known speakers, dry-run mode |
| `references/api.md` | API quick reference - input formats, size limits, response formats, known speaker notes |
| `agents/openai.yaml` | Agent interface definition - display name, icon, default prompt |
| `assets/transcribe.png` | Skill icon (large) |
| `assets/transcribe-small.svg` | Skill icon (small) |

## Scope Boundary

| Task | This skill? | Use instead |
|------|-------------|-------------|
| Transcribe audio/video file to text | YES | - |
| Label speakers in recorded meeting | YES | - |
| Identify known speakers by voice sample | YES | - |
| Batch transcribe multiple audio files | YES | - |
| Real-time speech-to-text streaming | NO | voice-ai-development |
| Voice agent with conversation flow | NO | voice-agents |
| Text-to-speech synthesis | NO | voice-ai-development |
| Telephony IVR or call routing | NO | twilio-communications |
| Audio noise reduction or editing | NO | standard audio tools |

## Model Selection Decision Matrix

First match wins. Stop at the first row where Signal is true.

| Signal | Model | Response Format | CLI flags |
|--------|-------|-----------------|-----------|
| Need speaker labels | gpt-4o-transcribe-diarize | diarized_json | `--model gpt-4o-transcribe-diarize --response-format diarized_json` |
| Known speakers to identify | gpt-4o-transcribe-diarize | diarized_json | above + `--known-speaker "Name=path.wav"` per speaker |
| Need timestamps in structured output | gpt-4o-mini-transcribe | json | `--response-format json` |
| Fast plain-text transcription (default) | gpt-4o-mini-transcribe | text | (no extra flags needed) |

## Audio Pre-Assessment

| Condition | Action | Why |
|-----------|--------|-----|
| Clean recording, single speaker | Transcribe directly with mini-transcribe | Fastest, cheapest path |
| Multiple speakers, labels needed | Use diarize model with diarized_json | Only model that produces speaker segments |
| Multiple speakers, labels NOT needed | Use mini-transcribe with text | Faster, diarization unnecessary |
| Audio >30 seconds | Keep `--chunking-strategy auto` (default) | Mandatory for diarize model; recommended for all long audio |
| Audio file >25MB | Split file before sending | Hard API limit, request will fail at 25MB |
| Background noise or low quality | Add `--language` hint for expected language | Helps model compensate; accuracy still degrades |
| Non-standard format | Convert to mp3/wav/m4a first | Supported: mp3, mp4, mpeg, mpga, m4a, wav, webm |

## Transcription Strategy Procedure

Follow this sequence for every transcription request. Do not skip steps.

1. **Assess audio characteristics**: Identify speaker count, recording quality, duration, and file format. Check file size against 25MB limit.
2. **Determine output needs**: Does the user need plain text, timestamps, or speaker labels? This determines the model and response format.
3. **Select model using Decision Matrix**: Match the first row where Signal is true. Do not default to diarize model "just in case" -- it is slower and more expensive.
4. **Validate with dry-run**: Run `--dry-run` first on any non-trivial request (multiple files, known speakers, unfamiliar audio format). This catches configuration errors before consuming API credits.
5. **Execute and verify**: After transcription, spot-check speaker attributions if diarized. Warn the user that labels are probabilistic for any critical attribution.

**Key mindset**: The most common mistake is jumping to the diarize model for any multi-speaker audio. If the user does not need speaker labels, mini-transcribe is faster, cheaper, and often more accurate for pure text output.

## CLI Reference

Script location: `~/.claude/skills/transcribe/scripts/transcribe_diarize.py`

**Prerequisite**: `uv pip install openai` (or `pip install openai`). OPENAI_API_KEY must be set in environment.

### By use case

**Simple transcription** (most common):
```bash
python ~/.claude/skills/transcribe/scripts/transcribe_diarize.py recording.mp3 --out transcript.txt
```

**Speaker-labeled meeting notes**:
```bash
python ~/.claude/skills/transcribe/scripts/transcribe_diarize.py meeting.m4a \
  --model gpt-4o-transcribe-diarize \
  --response-format diarized_json \
  --out-dir output/meeting
```

**Known speaker identification** (max 4 speakers):
```bash
python ~/.claude/skills/transcribe/scripts/transcribe_diarize.py interview.wav \
  --model gpt-4o-transcribe-diarize \
  --response-format diarized_json \
  --known-speaker "Alice=refs/alice.wav" \
  --known-speaker "Bob=refs/bob.wav" \
  --out-dir output/interview
```

**Batch transcription** (multiple files):
```bash
python ~/.claude/skills/transcribe/scripts/transcribe_diarize.py file1.mp3 file2.wav file3.m4a --out-dir output/batch
```

**Dry run** (validate inputs, print payload, no API call):
```bash
python ~/.claude/skills/transcribe/scripts/transcribe_diarize.py audio.mp3 --dry-run
```

## Diarization Gotchas

These are non-obvious constraints that cause silent failures or unexpected results:

1. **Max 4 known speaker references** -- API hard limit. The CLI enforces this. If you have more speakers, omit the least important and let the model assign generic labels.
2. **Prompting NOT supported with diarize model** -- `--prompt` flag with gpt-4o-transcribe-diarize causes an error. The CLI blocks this combination. Use `--language` hint instead for guidance.
3. **Known speaker refs must be audio, not text** -- The API needs voice samples (wav/mp3/m4a files) to match speakers. Text descriptions of voices do not work.
4. **diarized_json format ONLY works with diarize model** -- Using `--response-format diarized_json` with gpt-4o-mini-transcribe will fail. The CLI validates this.
5. **Speaker labels are probabilistic** -- The model guesses speaker boundaries. Short utterances (<2 seconds) and speakers with similar voices cause misattribution. Always verify critical speaker attributions manually.
6. **Chunking is mandatory for diarize model on long audio** -- The default `--chunking-strategy auto` handles this, but if overridden to none, audio >30s will fail with the diarize model.
7. **Known speaker audio quality matters** -- Reference clips should be clean, single-speaker audio of 5-15 seconds. Noisy or multi-speaker reference clips degrade matching accuracy significantly.

## Output Format Guide

| Format | Extension | Use for | Contains |
|--------|-----------|---------|----------|
| text | .txt | Direct reading, editing, summarization | Plain transcript text only |
| json | .json | Programmatic access, timestamp extraction | Structured segments with start/end times |
| diarized_json | .json | Meeting notes, interview analysis, attribution | Speaker-labeled segments with timestamps |

## Rationalization

| Concept | Why it is HERE and not in general knowledge |
|---------|----------------------------------------------|
| Model selection matrix (mini vs diarize) | OpenAI transcription models are new (2024-2025), selection criteria not widely documented, wrong choice = failed request |
| Known speaker reference mechanics | Underdocumented API feature using extra_body with base64 data URLs -- not guessable from standard SDK docs |
| diarized_json format constraints | Format-model coupling is a hard constraint that causes cryptic errors if violated |
| Chunking strategy requirements | Mandatory for diarize model on long audio but optional for mini -- asymmetric requirement not obvious |
| CLI script architecture | Bundled 277-line script with validation, dry-run, batch support -- must know it exists and how to invoke |
| Speaker attribution confidence | Probabilistic labeling with known failure modes (short utterances, similar voices) -- critical for meeting notes accuracy |

## Red Flags -- STOP and reassess

1. User wants real-time voice conversation -- this is file-based transcription, not streaming STT
2. User asks to generate speech from text -- this is speech-to-text only, not TTS
3. User needs telephony integration -- transcription is API-based, not phone-system-connected
4. Audio file exceeds 25MB -- must split before sending, cannot increase limit
5. User expects 100% speaker attribution accuracy -- labels are probabilistic, warn about verification
6. User wants to use --prompt with diarize model -- not supported, will error
7. User provides text descriptions instead of audio files for known speakers -- API requires audio samples
8. User needs transcription in a language the model may not support well -- set expectations about accuracy

## NEVER

1. NEVER call the OpenAI API directly when the bundled CLI script handles the use case -- the script has validation, error handling, and output formatting built in
2. NEVER use diarized_json response format with gpt-4o-mini-transcribe -- format requires the diarize model
3. NEVER pass --prompt flag with gpt-4o-transcribe-diarize -- prompting is not supported for this model
4. NEVER send audio files larger than 25MB without splitting first -- hard API limit, request will be rejected
5. NEVER present diarized speaker labels as ground truth -- labels are probabilistic and must be verified for critical attributions
