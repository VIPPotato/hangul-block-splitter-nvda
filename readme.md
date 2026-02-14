# Hangul Block Splitter NVDA Add-on

## Korean Follows Below / 한국어는 아래에 있습니다

## English

This repository contains an NVDA add-on version of Hangul Block Splitter.

It keeps the core behavior of the standalone app while fitting naturally into NVDA workflows.

- Splits Hangul syllable blocks into compatibility Jamo.
- Optional complex-letter split (`ㅘ -> ㅗㅏ`, `ㄳ -> ㄱㅅ`).
- Optional spacing between split letters.
- Splits selected Hangul text first (falls back to current line, then Hangul under cursor).
- Filters out non-Hangul characters automatically (including in the splitter dialog input).
- Provides a splitter dialog seeded from selection/current line/current character.
- Splitter dialog can be closed with `Escape`.
- Adds a Tools menu entry to open the splitter without gestures.
- All commands are exposed in NVDA Input Gestures for rebinding.

### Default gestures

- `NVDA+alt+h`: Describe characters of split selected Hangul text (or current line, or Hangul under cursor).  
  Press twice to copy the split result to clipboard.
- `NVDA+shift+h`: Open splitter dialog.

### Rebinding gestures

Go to NVDA menu -> Preferences -> Input Gestures, then find category `Hangul Block Splitter`.

Commands without default gestures can also be bound there:

- Copy split result to clipboard
- Toggle complex-letter splitting
- Toggle insertion of spaces
- Toggle live update in dialog

### Add-on settings

Go to NVDA menu -> Preferences -> Settings -> `Hangul Block Splitter`.

- Default complex-letter splitting
- Default spacing between letters
- Default live update behavior in dialog

### Build `.nvda-addon`

```powershell
pwsh -ExecutionPolicy Bypass -File .\scripts\build_addon.ps1
```

The build output is created in `dist\`.

## 한국어

이 저장소는 Hangul Block Splitter를 NVDA 추가 기능으로 옮긴 구현입니다.

기존 독립 실행형 앱의 핵심 기능은 유지하면서, NVDA 사용 흐름에 자연스럽게 맞게 구성했습니다.

- 한글 음절 블록을 호환 자모로 분해
- 겹모음/겹받침 추가 분해 옵션 (`ㅘ -> ㅗㅏ`, `ㄳ -> ㄱㅅ`)
- 분해 결과 글자 사이 공백 삽입 옵션
- 선택된 한글 전체를 우선 분해하고, 선택이 없으면 커서 아래 한글을 분해
- 선택이 없을 때 현재 줄을 먼저 분해하고, 그래도 없으면 커서 아래 한글을 분해
- 한글이 아닌 문자는 자동으로 제외(분해기 대화상자 입력 포함)
- 선택 텍스트/현재 줄/현재 글자를 기반으로 분해 대화상자 열기
- 분해기 대화상자는 `Escape` 키로 닫기 가능
- 도구 메뉴에서 제스처 없이도 분해기 열기 가능
- NVDA 입력 제스처에서 모든 명령 재할당 가능

### 기본 제스처

- `NVDA+alt+h`: 선택된 한글(없으면 현재 줄, 그래도 없으면 커서 아래 한글)을 분해해 문자 설명으로 읽기  
  두 번 누르면 분해 결과를 클립보드에 복사
- `NVDA+shift+h`: 한글 분해기 대화상자 열기

### 제스처 재할당

NVDA 메뉴 -> 환경설정 -> 입력 제스처에서 `한글 블록 분해기` 범주를 찾으면 됩니다.

기본 제스처가 없는 명령도 여기서 직접 연결할 수 있습니다.

- 분해 결과 클립보드 복사
- 겹글자 분해 켜기/끄기
- 글자 사이 공백 삽입 켜기/끄기
- 대화상자 실시간 갱신 켜기/끄기

### 추가 기능 설정

NVDA 메뉴 -> 환경설정 -> 설정 -> `한글 블록 분해기` 패널에서 기본값을 바꿀 수 있습니다.

- 겹글자 분해 기본값
- 공백 삽입 기본값
- 대화상자 실시간 갱신 기본값

### `.nvda-addon` 빌드

```powershell
pwsh -ExecutionPolicy Bypass -File .\scripts\build_addon.ps1
```

빌드 결과 파일은 `dist\` 폴더에 생성됩니다.
