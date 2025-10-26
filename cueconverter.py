#!/usr/bin/env python3
"""
CueConverter v1.0
Convert cue files to individual tracks using FFcuesplitter.
"""

import os
import sys
import subprocess
from pathlib import Path
from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter

# Path completer for tab completion
path_completer = PathCompleter()

def get_cue_file():
    """Prompt user for cue file path with tab completion."""
    while True:
        cue_path = prompt("cue 파일 경로를 입력하세요 (종료하려면 'q'): ", completer=path_completer).strip()
        if cue_path.lower() == 'q':
            return None
        if os.path.isfile(cue_path) and cue_path.lower().endswith('.cue'):
            return cue_path
        print("유효하지 않은 cue 파일입니다. 유효한 .cue 파일 경로를 입력하세요.")

def get_output_format():
    """Prompt user for output format."""
    formats = ['mp3', 'flac', 'wav', 'aac', 'ogg']
    print("사용 가능한 형식:", ', '.join(formats))
    while True:
        fmt = input("출력 형식을 입력하세요: ").strip().lower()
        if fmt in formats:
            return fmt
        print("유효하지 않은 형식입니다. 다음 중 선택하세요:", ', '.join(formats))

def get_quality():
    """Prompt user for quality setting."""
    qualities = ['high', 'medium', 'low']
    print("사용 가능한 음질:", ', '.join(qualities))
    while True:
        qual = input("음질을 입력하세요: ").strip().lower()
        if qual in qualities:
            return qual
        print("유효하지 않은 음질입니다. 다음 중 선택하세요:", ', '.join(qualities))

def parse_cue_file(cue_path):
    """Parse cue file to extract track information."""
    try:
        with open(cue_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"cue 파일 읽기 오류: {e}")
        return []
    
    tracks = []
    discnumber = "01"
    current_track = None
    
    for line in lines:
        line = line.strip()
        if line.upper().startswith('REM DISCNUMBER'):
            discnumber = line.split()[-1].zfill(2)
        elif line.upper().startswith('TRACK'):
            if current_track:
                tracks.append(current_track)
            track_num = line.split()[1].zfill(2)
            current_track = {'disc': discnumber, 'track': track_num, 'title': '', 'start': 0, 'duration': None}
        elif line.upper().startswith('TITLE') and current_track:
            title = line.split('TITLE')[1].strip()
            if title.startswith('"') and title.endswith('"'):
                title = title[1:-1]
            current_track['title'] = title
        elif line.upper().startswith('INDEX 01') and current_track:
            time_str = line.split()[-1]  # MM:SS:FF
            mm, ss, ff = map(int, time_str.split(':'))
            frames = (mm * 60 + ss) * 75 + ff
            current_track['start'] = frames
    
    if current_track:
        tracks.append(current_track)
    
    # Calculate durations
    for i, track in enumerate(tracks):
        if i < len(tracks) - 1:
            next_start = tracks[i+1]['start']
            track['duration'] = next_start - track['start']
        else:
            track['duration'] = None  # Last track
    
    return tracks

def convert_tracks(cue_path, output_format, quality, tracks):
    """Convert tracks using FFmpeg."""
    output_dir = Path.cwd() / "output"
    output_dir.mkdir(exist_ok=True)
    
    # Find the audio file (assume same name as cue but .wav)
    audio_file = cue_path.replace('.cue', '.wav')
    if not os.path.isfile(audio_file):
        print(f"오디오 파일 {audio_file}을(를) 찾을 수 없습니다.")
        return
    
    # Quality settings
    bitrate_map = {'low': '128k', 'medium': '192k', 'high': '320k'}
    bitrate = bitrate_map.get(quality, '192k')
    
    codec_map = {
        'mp3': 'libmp3lame',
        'flac': 'flac',
        'wav': 'pcm_s16le',
        'aac': 'aac',
        'ogg': 'libvorbis'
    }
    codec = codec_map.get(output_format, 'libmp3lame')
    
    for track in tracks:
        # Sanitize title for filename
        safe_title = track['title'].replace(' ', '_').replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
        output_file = output_dir / f"{track['disc']}-{track['track']}.{safe_title}.{output_format}"
        start_time = track['start'] / 75.0  # Convert frames to seconds
        
        cmd = [
            'ffmpeg', '-i', audio_file,
            '-ss', str(start_time),
            '-acodec', codec
        ]
        if track['duration']:
            cmd.extend(['-t', str(track['duration'] / 75.0)])
        if output_format == 'mp3':
            cmd.extend(['-ab', bitrate])
        elif output_format in ['aac', 'ogg']:
            cmd.extend(['-b:a', bitrate])
        cmd.extend(['-progress', 'pipe:1', '-y', str(output_file)])  # -y to overwrite, progress to stdout
        
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
            total_duration = track['duration'] / 75.0 if track['duration'] else None
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    line = output.strip()
                    if line.startswith('out_time='):
                        time_str = line.split('=')[1]
                        # Parse time like 00:00:12.34
                        h, m, s = map(float, time_str.split(':'))
                        current_time = h * 3600 + m * 60 + s
                        if total_duration:
                            progress = min(100, (current_time / total_duration) * 100)
                            print(f"\r트랙 {track['track']} 진행율: {progress:.1f}%", end='', flush=True)
            
            if process.returncode == 0:
                print(f"\n변환됨: {output_file.name}")
            else:
                stderr_msg = process.stderr.read()
                print(f"\n트랙 {track['track']} 변환 오류: {stderr_msg}")
        except Exception as e:
            print(f"트랙 {track['track']} 변환 오류: {e}")

def check_dependencies():
    """Check if required dependencies are available."""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("오류: FFmpeg가 설치되어 있지 않습니다. FFmpeg를 설치하세요.")
        return False
    return True

def main():
    print("CueConverter v1.0")
    if not check_dependencies():
        return
    
    while True:
        cue_file = get_cue_file()
        if cue_file is None:
            break
        
        output_format = get_output_format()
        quality = get_quality()
        
        tracks = parse_cue_file(cue_file)
        if not tracks:
            print("cue 파일에서 트랙을 찾을 수 없습니다.")
            continue
        
        convert_tracks(cue_file, output_format, quality, tracks)
        print("변환이 완료되었습니다. 다시 시작합니다...")

if __name__ == "__main__":
    main()