#!/usr/bin/env python3
"""Bounded-memory range reader and PCM WAV writer for supported audio formats."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import wave
from typing import Any


@dataclass(frozen=True)
class AudioSourceInfo:
    framerate: int
    nchannels: int
    frames: int
    source_format: str
    source_subtype: str
    sampwidth: int


def audio_source_info(path: Path) -> AudioSourceInfo:
    """Read decoder metadata without decoding the audio stream."""
    path = Path(path)
    try:
        import soundfile as sf
        info = sf.info(str(path))
        subtype = str(info.subtype or "UNKNOWN")
        width = {
            "PCM_U8": 1, "PCM_16": 2, "PCM_24": 3, "PCM_32": 4,
            "FLOAT": 4, "DOUBLE": 8,
        }.get(subtype, 0)
        if info.samplerate <= 0 or info.channels <= 0 or info.frames <= 0:
            raise ValueError("Empty or invalid audio source")
        return AudioSourceInfo(
            int(info.samplerate), int(info.channels), int(info.frames),
            str(info.format or path.suffix.lstrip(".").upper()), subtype, width,
        )
    except ImportError:
        if path.suffix.lower() not in {".wav", ".wave"}:
            raise RuntimeError("Non-WAV extraction requires python-soundfile and libsndfile codec support")
        with wave.open(str(path), "rb") as audio:
            if audio.getcomptype() != "NONE":
                raise ValueError("Compressed WAV requires python-soundfile")
            return AudioSourceInfo(
                audio.getframerate(), audio.getnchannels(), audio.getnframes(),
                "WAV", "PCM", audio.getsampwidth(),
            )


def write_pcm_wav_range(
    source: Path,
    start_frame: int,
    end_frame: int,
    destination: Path,
    *,
    expected_rate: int | None = None,
) -> dict[str, Any]:
    """Write an exact source frame range as a new 24-bit PCM WAV.

    Decodes at most 65,536 frames at a time. The destination is created
    exclusively and partial output is removed on failure.
    """
    import soundfile as sf

    source = Path(source)
    destination = Path(destination)
    info = audio_source_info(source)
    if start_frame < 0 or end_frame <= start_frame or end_frame > info.frames:
        raise ValueError("Requested audio range is outside the source")
    if expected_rate is not None and int(expected_rate) != info.framerate:
        raise ValueError("Analysis sample rate no longer matches source")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite {destination}")
    try:
        # Stream in bounded chunks: a long riff/phrase must not allocate the
        # entire decoded range in RAM on the target 8 GB / dual-core PC.
        remaining = end_frame - start_frame
        with sf.SoundFile(str(source), mode="r") as reader:
            reader.seek(start_frame)
            with sf.SoundFile(
                str(destination), mode="x",
                samplerate=info.framerate, channels=info.nchannels,
                format="WAV", subtype="PCM_24",
            ) as writer:
                while remaining:
                    count = min(65536, remaining)
                    data = reader.read(count, dtype="float32", always_2d=True)
                    if len(data) != count:
                        raise IOError("Decoder returned an incomplete frame range")
                    writer.write(data)
                    remaining -= count
        with sf.SoundFile(str(destination), mode="r") as verify:
            if (len(verify) != end_frame - start_frame
                    or verify.samplerate != info.framerate
                    or verify.channels != info.nchannels
                    or verify.subtype != "PCM_24"):
                raise IOError("Derived WAV failed frame/rate/channel/PCM verification")
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    return {
        "sample_rate": info.framerate,
        "channels": info.nchannels,
        "sample_width_bytes": 3,
        "frame_count": end_frame - start_frame,
        "source_format": info.source_format,
        "source_subtype": info.source_subtype,
        "derived_format": "WAV",
        "derived_subtype": "PCM_24",
    }
