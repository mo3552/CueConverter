# CueConverter v1.0

CueConverter는 cue 파일을 사용하여 단일 WAV 파일을 트랙별로 분할하여 원하는 음악 파일 형식으로 변환하는 Python 프로그램입니다.

## 요구사항

-   Python 3.7+
-   FFmpeg (설치되어 PATH에 있어야 함)
-   가상 환경 .venv

## 설치

1. Python 가상 환경 활성화:

    ```
    .venv\Scripts\activate
    ```

2. 필요한 패키지 설치:
    ```
    pip install -r requirements.txt
    ```

## 사용법

1. 프로그램 실행:

    **권장: `dist\cueconverter.exe`를 더블클릭하여 실행 (독립 실행 파일, 별도 설치 불필요)**

    또는 배치 파일: `run_cueconverter.bat`

    또는 수동으로:

    ```
    .venv\Scripts\activate
    python cueconverter.py
    ```

2. cue 파일 경로 입력 (탭 완성 지원):

    - 유효한 .cue 파일 경로를 입력하세요.

3. 출력 형식 선택 (mp3, flac, wav, aac, ogg)

4. 음질 선택 (high, medium, low)

5. 변환 완료 후 프로그램이 다시 시작됩니다. 종료하려면 'q' 입력.

## 출력

트랙은 `.\output` 디렉토리에 `<discnumber>-<track>.<title>.<extension>` 형식으로 저장됩니다.

## 주의사항

-   cue 파일과 동일한 이름의 WAV 파일이 같은 디렉토리에 있어야 합니다.
-   FFmpeg가 설치되어 있어야 합니다.
-   트랙 제목의 공백과 특수 문자는 파일명에서 언더스코어(\_)로 대체됩니다.
