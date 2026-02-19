# Hangul Block Splitter

Hangul Block Splitter is an NVDA add-on that breaks Hangul syllable blocks into Jamo and lets you read, describe, or copy the split result quickly.

## Features

- Splits selected Hangul text first.
- If nothing is selected, uses your configured default scope: single block under cursor, current word, or current line.
- Accepts and processes only Hangul script characters; non-Hangul input is ignored.
- Supports optional complex-letter splitting (`ㅘ -> ㅗㅏ`, `ㄳ -> ㄱㅅ`).
- Supports optional spacing between split letters.
- Includes a splitter dialog with editable input and read-only output.
- Lets you close the splitter dialog with `Escape`.
- Adds a Tools menu item so you can open the splitter without a gesture.
- Exposes all commands in Input Gestures so you can rebind them freely.

## Default gestures

- `NVDA+alt+h`: Describe characters of split selected Hangul text (or the configured default scope under cursor). Press twice to copy the split result to clipboard.
- `NVDA+ctrl+h`: Copy split selected Hangul text (or the configured default scope under cursor) to clipboard.
- `NVDA+shift+h`: Open the splitter dialog.

## Rebinding gestures

Go to NVDA menu -> Preferences -> Input Gestures, then find the `Hangul Block Splitter` category.

You can also bind commands that have no default gesture:

- Toggle complex-letter splitting
- Toggle insertion of spaces
- Toggle live update in dialog
- Cycle default split scope (single block / word / line)

## Add-on settings

Go to NVDA menu -> Preferences -> Settings -> `Hangul Block Splitter`.

- Default complex-letter splitting
- Default spacing between letters
- Default live update behavior in dialog
- Default split scope when no text is selected
