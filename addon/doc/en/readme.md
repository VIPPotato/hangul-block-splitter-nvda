# Hangul Block Splitter

Hangul Block Splitter is an NVDA add-on that breaks Hangul syllable blocks into Jamo, provides phonetic spelling mnemonics, looks up Hanja stroke counts and meanings, and lets you read, inspect, or copy results quickly.

## Features

- Splits selected Hangul text first.
- If nothing is selected, uses your configured default scope: single block under cursor, current word, or current line.
- Accepts and processes Hangul and Hanja characters; other characters are ignored.
- Supports optional complex-letter splitting (`ㅘ -> ㅗㅏ`, `ㄳ -> ㄱㅅ`, `ㅄ -> ㅂㅅ`).
- Supports optional spacing between split letters.
- **Phonetic Spelling Output Modes**:
  - **Off**: Standard Jamo names (e.g. `ㄱ -> 기역`).
  - **Short phonetic words**: Standard Korean screen reader mnemonics (e.g. `ㄱ -> 가을`, `ㅗ -> 오이`, `ㄳ -> 가을 서울`).
  - **Full phonetic descriptions**: Full mnemonic descriptions (e.g. `ㄱ -> 가을 기역`, `ㄳ -> 기역시옷: 가을, 서울`).
- **Inline Review & Hanja Inspection (`NVDA+shift+g`)**:
  - Inspects text at selection, review cursor, or caret position.
  - Decomposes Hangul blocks with phonetic spelling.
  - Looks up Hanja characters with Korean reading, meaning (훈음), and stroke count.
  - Press once to hear; press twice to copy to the clipboard.
- **Built-in Offline Hanja Dictionary**: 27,786 Chinese characters with reading, meaning, and stroke count (e.g. `家: 집 가, 10획`).
- Includes a splitter dialog with editable input and read-only output.
- Lets you close the splitter dialog with `Escape`.
- Adds a Tools menu item so you can open the splitter without a gesture.
- Exposes all commands in Input Gestures so you can rebind them freely.

## Default gestures

- `NVDA+shift+g`: Inline decomposition / Hanja inspection at review cursor, caret, or selection. Press twice to copy result to clipboard.
- `NVDA+shift+h`: Open the splitter dialog.
- `NVDA+alt+h`: Describe characters of split selected Hangul text (or the configured default scope under cursor). Press twice to copy the split result to clipboard.
- `NVDA+ctrl+h`: Cycle default split scope when no text is selected (single block / word / line).

## Rebinding gestures

Go to NVDA menu -> Preferences -> Input Gestures, then find the `Hangul Block Splitter` category.

You can also bind commands that have no default gesture:

- Cycle phonetic spelling mode (Off / Short / Full)
- Copy split result to clipboard
- Toggle complex-letter splitting
- Toggle insertion of spaces
- Toggle live update in dialog

## Add-on settings

Go to NVDA menu -> Preferences -> Settings -> `Hangul Block Splitter`.

- Default complex-letter splitting
- Default spacing between letters
- Default live update behavior in dialog
- Default split scope when no text is selected
- Default phonetic description mode
