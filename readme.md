# Hangul Block Splitter NVDA Add-on

## Korean Follows Below / 한국어는 아래에 있습니다

## English

This repository contains an NVDA add-on version of Hangul Block Splitter.

It keeps the core behavior of the standalone app while fitting naturally into NVDA workflows.

- Splits Hangul syllable blocks into compatibility Jamo.
- Optional complex-letter split (`ㅘ -> ㅗㅏ`, `ㄳ -> ㄱㅅ`, `ㅄ -> ㅂㅅ`).
- Optional spacing between split letters.
- **Phonetic Spelling Output Modes**:
  - **Off**: Standard Jamo names (e.g., `ㄱ -> 기역`).
  - **Short phonetic words**: Familiar Korean screen reader mnemonic words (e.g., `ㄱ -> 가을`, `ㅗ -> 오이`, `ㄳ -> 가을 서울`).
  - **Full phonetic descriptions**: Rich mnemonic descriptions (e.g., `ㄱ -> 가을 기역`, `ㄳ -> 기역시옷: 가을, 서울`).
- **Inline Review & Hanja Inspection (`NVDA+shift+g`)**:
  - Inspects text at selection, review cursor, or caret position.
  - Spells out Hangul blocks with phonetic/Jamo decomposition.
  - Looks up Hanja characters against a built-in dictionary (reading, meaning, and stroke count).
  - Press once to hear the description; press twice to copy the result to the clipboard.
- **Offline Hanja Dictionary**: 27,786 Chinese characters with Korean pronunciation, meaning (훈음), and total stroke count (e.g. `家: 집 가, 10획`).
- Splits selected text first; if nothing is selected, uses a configurable default scope: single block under cursor, current word, or current line.
- Filters out non-Hangul/Hanja characters automatically (including in the splitter dialog input).
- Provides a splitter dialog seeded from selection or the configured default scope.
- Splitter dialog can be closed with `Escape`.
- Adds a Tools menu entry to open the splitter without gestures.
- All commands are exposed in NVDA Input Gestures for rebinding.

### Default gestures

- `NVDA+shift+g`: Inline decomposition / Hanja inspection at review cursor, caret, or selection.  
  Press twice to copy the result to clipboard.
- `NVDA+shift+h`: Open splitter dialog.
- `NVDA+alt+h`: Describe characters of split selected Hangul text (or configured default scope under cursor).  
  Press twice to copy the split result to clipboard.
- `NVDA+ctrl+h`: Cycle default split scope when no text is selected (single block / word / line).

### Rebinding gestures

Go to NVDA menu -> Preferences -> Input Gestures, then find category `Hangul Block Splitter`.

Commands without default gestures can also be bound there:

- Cycle phonetic spelling mode (Off / Short / Full)
- Copy split result to clipboard
- Toggle complex-letter splitting
- Toggle insertion of spaces
- Toggle live update in dialog

### Add-on settings

Go to NVDA menu -> Preferences -> Settings -> `Hangul Block Splitter`.

- Default complex-letter splitting
- Default spacing between letters
- Default live update behavior in dialog
- Default split scope when no text is selected
- Default phonetic description mode

### Build `.nvda-addon`

```powershell
pwsh -ExecutionPolicy Bypass -File .\scripts\build_addon.ps1
```

The build output is created in `dist\`.

## 한국어

이 저장소는 Hangul Block Splitter를 NVDA 추가 기능으로 옮긴 구현입니다.

기존 독립 실행형 앱의 핵심 기능은 유지하면서, NVDA 사용 흐름에 자연스럽게 맞게 구성했습니다.

- 한글 음절 블록을 호환 자모로 분해
- 겹모음/겹받침 추가 분해 옵션 (`ㅘ -> ㅗㅏ`, `ㄳ -> ㄱㅅ`, `ㅄ -> ㅂㅅ`)
- 분해 결과 글자 사이 공백 삽입 옵션
- **단어 설명(음성 풀이) 모드 지원**:
  - **꺼짐**: 표준 자모 이름 (예: `ㄱ -> 기역`)
  - **짧은 단어 설명**: 스크린 리더 표준 연상 단어 (예: `ㄱ -> 가을`, `ㅗ -> 오이`, `ㄳ -> 가을 서울`)
  - **상세 단어 설명**: 상세 풀이 (예: `ㄱ -> 가을 기역`, `ㄳ -> 기역시옷: 가을, 서울`)
- **인라인 검토 및 한자 풀이 (`NVDA+shift+g`)**:
  - 선택 영역, 검토 커서 위치 또는 캐럿 위치의 글자를 바로 분해/조회
  - 한글은 설정된 단어 설명 모드로 풀어 읽기
  - 한자는 내장 사전을 통해 훈음과 획수를 즉시 확인
  - 한 번 누르면 음성 출력, 두 번 누르면 결과를 클립보드에 복사
- **오프라인 한자 사전 탑재**: 27,786자의 한자 음, 훈음(뜻과 소리), 총 획수 정보 내장 (예: `家: 집 가, 10획`)
- 선택한 한글이 있으면 그 범위를 우선 분해하며, 선택이 없을 때는 설정한 기본 범위(커서 아래 한 글자/현재 단어/현재 줄)로 분해
- 한글/한자가 아닌 문자는 자동으로 제외(분해기 대화상자 입력 포함)
- 선택 텍스트 또는 설정한 기본 범위를 기반으로 분해 대화상자 열기
- 분해기 대화상자는 `Escape` 키로 닫기 가능
- 도구 메뉴에서 제스처 없이도 분해기 열기 가능
- NVDA 입력 제스처에서 모든 명령 재할당 가능

### 기본 제스처

- `NVDA+shift+g`: 현재 위치(선택 영역, 검토 커서 또는 캐럿)의 한글 음성 풀이 분해 및 한자 훈음/획수 확인  
  두 번 누르면 결과를 클립보드에 복사
- `NVDA+shift+h`: 한글 분해기 대화상자 열기
- `NVDA+alt+h`: 선택한 한글(선택이 없으면 설정한 기본 범위)을 분해해 문자 설명으로 읽기  
  두 번 누르면 분해 결과를 클립보드에 복사
- `NVDA+ctrl+h`: 텍스트 미선택 시 기본 분해 범위를 순환 전환(한 글자/단어/줄)

### 제스처 재할당

NVDA 메뉴 -> 환경설정 -> 입력 제스처에서 `한글 블록 분해기` 범주를 찾으면 됩니다.

기본 제스처가 없는 명령도 여기서 직접 연결할 수 있습니다.

- 단어 설명 모드 순환 전환 (꺼짐 / 짧은 단어 설명 / 상세 단어 설명)
- 분해 결과 클립보드 복사
- 겹글자 분해 켜기/끄기
- 글자 사이 공백 삽입 켜기/끄기
- 대화상자 실시간 갱신 켜기/끄기

### 추가 기능 설정

NVDA 메뉴 -> 환경설정 -> 설정 -> `한글 블록 분해기` 패널에서 기본값을 바꿀 수 있습니다.

- 겹글자 분해 기본값
- 공백 삽입 기본값
- 대화상자 실시간 갱신 기본값
- 텍스트 미선택 시 기본 분해 범위
- 단어 설명 모드 기본값

### `.nvda-addon` 빌드

```powershell
pwsh -ExecutionPolicy Bypass -File .\scripts\build_addon.ps1
```

빌드 결과 파일은 `dist\` 폴더에 생성됩니다.
