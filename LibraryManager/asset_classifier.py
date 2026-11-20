#!/usr/bin/env python3
"""Conservative WAV asset classifier using envelope and optional pitch-event evidence."""
from __future__ import annotations
import argparse, json, math, statistics
from pathlib import Path
from audio_analysis import read_mono_pcm

def _median(values):
    return statistics.median(values) if values else 0.0

def _envelope(samples, rate, decimation, frame_ms=20, hop_ms=10):
    frame=max(1,round(rate*frame_ms/1000/decimation))
    hop=max(1,round(rate*hop_ms/1000/decimation))
    env=[]
    for start in range(0,max(1,len(samples)-frame+1),hop):
        chunk=samples[start:start+frame]
        if len(chunk)!=frame: break
        env.append(math.sqrt(sum(x*x for x in chunk)/frame))
    return env,hop_ms/1000.0

def _onsets(env, dt):
    if len(env)<3: return []
    floor=max(0.006,max(env)*0.10)
    rises=[max(0.0,env[i]-env[i-1]) for i in range(1,len(env))]
    positive=[x for x in rises if x>0]
    # Use a lower robust threshold: median positive slope can be large for
    # decaying one-shot pulses, so multiplying it by 2.5 suppresses real attacks.
    threshold=max(0.004,_median(positive)*0.70,max(rises,default=0)*0.12)
    result=[]; last=-10**9
    for i,rise in enumerate(rises,1):
        if rise>=threshold and env[i]>=floor and (i-last)*dt>=0.075:
            result.append(i*dt); last=i
    return result

def _regularity(onsets):
    intervals=[b-a for a,b in zip(onsets,onsets[1:])]
    if len(intervals)<2: return 0.0
    mean=statistics.fmean(intervals)
    return max(0.0,min(1.0,1.0-statistics.pstdev(intervals)/mean)) if mean else 0.0

def _pitch_evidence(path):
    # Optional monophonic tracker: pitch hypotheses enrich subtype classification,
    # but never override the need for listening/review on polyphonic guitar.
    try:
        from pitch_events import analyze_pitch_events
        result=analyze_pitch_events(path)
        events=result.get("pitch_events",[])
        notes=[e["midi_note_candidate"] for e in events]
        unique=[]
        for note in notes:
            if not unique or unique[-1]!=note: unique.append(note)
        return {"events":events,"note_sequence":unique,
                "distinct_pitch_count":len(set(unique)),
                "pitch_tracker":"YIN_MONOPHONIC_CANDIDATES"}
    except (ValueError, OSError, ArithmeticError) as exc:
        return {"events":[],"note_sequence":[],"distinct_pitch_count":0,
                "pitch_tracker":"UNAVAILABLE","error":str(exc)}

def classify_wav(path: Path, short_max_seconds: float=1.25,
                 long_min_seconds: float=1.5, analyze_pitch: bool=True) -> dict:
    path=Path(path)
    samples,rate,frames,channels,width,decimation=read_mono_pcm(path)
    if rate<=0 or frames<=0 or not samples: raise ValueError("Empty or invalid WAV")
    duration=frames/rate
    env,dt=_envelope(samples,rate,decimation)
    peak=max((abs(x) for x in samples),default=0.0)
    active=[x for x in env if x>max(0.003,peak*0.025)]
    onsets=_onsets(env,dt) if peak>=0.003 and active else []
    regularity=_regularity(onsets)
    pitch=_pitch_evidence(path) if analyze_pitch and peak>=0.003 else {
        "events":[],"note_sequence":[],"distinct_pitch_count":0,"pitch_tracker":"SKIPPED"}
    note_sequence=pitch["note_sequence"]
    distinct=pitch["distinct_pitch_count"]
    pitch_event_count=len(pitch["events"])
    if peak<0.003 or not active:
        kind,subtype,confidence="UNKNOWN","UNKNOWN",0.99
        evidence=["No meaningful signal energy detected."]
    elif duration<=short_max_seconds and len(onsets)<=2:
        kind,subtype="ONE_SHOT","NOTE_ONE_SHOT"
        confidence=0.78 if duration<=0.65 else 0.68
        evidence=["Short duration and few envelope attacks support a one-shot candidate."]
    elif duration>=long_min_seconds:
        kind="SAMPLE"
        if len(onsets)>=3 and regularity>=0.55:
            if distinct>=3 and pitch_event_count>=4:
                subtype="RHYTHMIC_MELODY"
                confidence=min(0.90,0.68+regularity*0.15)
                evidence=["Repeated rhythmic attacks plus multiple changing pitch candidates indicate a rhythmic melodic sample."]
            elif distinct<=2:
                subtype="RHYTHM_PATTERN"
                confidence=min(0.90,0.68+regularity*0.18)
                evidence=["Repeated, stable rhythmic attack pattern with no substantial pitch sequence change."]
            else:
                subtype="RHYTHMIC_UNRESOLVED"
                confidence=0.60
                evidence=["Regular attack pattern detected, but pitch evidence is insufficient to distinguish a fixed rhythm pattern from a melodic rhythm."]
        elif distinct>=3 and pitch_event_count>=3:
            subtype="MELODIC"
            confidence=0.65
            evidence=["Several changing pitch candidates detected; a clear repeated rhythmic pulse was not established."]
        elif len(onsets)>=3:
            subtype="MULTI_HIT"; confidence=0.68
            evidence=["Long recording contains several separated attack candidates without stable rhythmic periodicity."]
        elif _median(env[-max(1,round(0.15/dt)):]) / max(peak,1e-9)>=0.35:
            subtype="SUSTAIN"; confidence=0.70
            evidence=["Long sustained energy without a clear repeated attack pattern."]
        else:
            subtype="UNKNOWN"; confidence=0.52
            evidence=["Long recording; subtype is not supported by current evidence."]
    else:
        kind,subtype,confidence="UNKNOWN","UNKNOWN",0.48
        evidence=["Duration and envelope evidence do not clearly separate a one-shot from a sample."]
    loop_candidate=bool(kind=="SAMPLE" and subtype in ("RHYTHM_PATTERN","RHYTHMIC_MELODY") and regularity>=0.75 and len(onsets)>=5)
    evidence += [f"Duration {duration:.3f}s; {len(onsets)} envelope attack candidates; rhythmic regularity {regularity:.2f}.",
                 f"Pitch tracker: {pitch['pitch_tracker']}; {pitch_event_count} pitch events; {distinct} distinct pitch candidates."]
    # Metadata-only note cut suggestions. No audio is physically split here.
    fragment_candidates = []
    for event in pitch.get("events", []):
        fragment_candidates.append({
            "fragment_id": f"NOTE-{len(fragment_candidates)+1:04d}",
            "fragment_type_candidate": "NOTE",
            "start_seconds": event["start_seconds"],
            "end_seconds": event["end_seconds"],
            "duration_seconds": event["duration_seconds"],
            "midi_note_candidate": event["midi_note_candidate"],
            "note_name_candidate": event["note_name_candidate"],
            "confidence": event["mean_confidence"],
            "review_status": "NEEDS_MUSICAL_REVIEW"
        })
    if subtype == "RHYTHM_PATTERN":
        content_type = "REPEATING_GUITAR_RHYTHM"
    elif subtype == "RHYTHMIC_MELODY":
        content_type = "GUITAR_MELODY_WITH_RHYTHMIC_PULSE"
    elif subtype == "MELODIC":
        content_type = "GUITAR_MELODY"
    elif subtype == "SUSTAIN":
        content_type = "SUSTAINED_TONE_OR_CHORD"
    elif subtype == "MULTI_HIT":
        content_type = "MULTIPLE_GUITAR_HITS"
    else:
        content_type = "UNRESOLVED_GUITAR_AUDIO"
    return {
        "classifier_version":"0.3.0",
        "source":str(path.resolve()),"duration_seconds":round(duration,6),
        "asset_kind_candidate":kind,"sample_subtype_candidate":subtype,
        "content_type_candidate":content_type,
        "rhythm_behavior_candidate":("REPEATING_STABLE_PATTERN" if subtype=="RHYTHM_PATTERN" else
                                     "RHYTHMIC_PITCH_SEQUENCE" if subtype=="RHYTHMIC_MELODY" else "UNRESOLVED"),
        "fragment_candidates": fragment_candidates,
        "fragment_count": len(fragment_candidates),
        "fragment_policy": "METADATA_CUT_PROPOSALS_ONLY",
        "loop_candidate":loop_candidate,
        "loop_status":"CANDIDATE_ONLY" if loop_candidate else "NOT_ESTABLISHED",
        "classification_confidence":round(confidence,3),"evidence":evidence,
        "features":{"onset_count":len(onsets),"onset_times_seconds":[round(x,4) for x in onsets],
                    "inter_onset_regularity":round(regularity,3),"pitch_event_count":pitch_event_count,
                    "distinct_pitch_count":distinct,"pitch_sequence":note_sequence},
        "review_status":"NEEDS_MUSICAL_REVIEW","license_status":"UNREVIEWED",
        "source_modified":False,
        "limitations":[
            "Envelope periodicity describes repeated attacks, not by itself a verified musical bar or groove.",
            "RHYTHM_PATTERN versus RHYTHMIC_MELODY uses monophonic pitch hypotheses; chords and distorted guitar may be unresolved.",
            "A changing pitch sequence may be a riff, chord voicing, noise or tracker error and requires listening.",
            "A loop candidate is not a confirmed seamless loop; phrase identity and boundary periodicity require separate checks.",
            "No source file is moved, renamed, deleted, extracted or modified."
        ]
    }

def main():
    parser=argparse.ArgumentParser(description="Classify WAV asset kind and rhythmic/pitch behavior.")
    parser.add_argument("wav",type=Path); parser.add_argument("--output",type=Path)
    parser.add_argument("--short-max",type=float,default=1.25)
    parser.add_argument("--long-min",type=float,default=1.5)
    parser.add_argument("--skip-pitch",action="store_true",help="Use envelope-only classification.")
    args=parser.parse_args()
    result=classify_wav(args.wav,args.short_max,args.long_min,not args.skip_pitch)
    payload=json.dumps(result,ensure_ascii=False,indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(payload,encoding="utf-8")
    print(payload); return 0

if __name__=="__main__": raise SystemExit(main())
