from __future__ import annotations

from dataclasses import dataclass

S_BASE = 0xAC00
S_END = 0xD7A3
L_COUNT = 19
V_COUNT = 21
T_COUNT = 28
N_COUNT = V_COUNT * T_COUNT

LEADING_COMPAT = (
	"ㄱ",
	"ㄲ",
	"ㄴ",
	"ㄷ",
	"ㄸ",
	"ㄹ",
	"ㅁ",
	"ㅂ",
	"ㅃ",
	"ㅅ",
	"ㅆ",
	"ㅇ",
	"ㅈ",
	"ㅉ",
	"ㅊ",
	"ㅋ",
	"ㅌ",
	"ㅍ",
	"ㅎ",
)

VOWEL_COMPAT = (
	"ㅏ",
	"ㅐ",
	"ㅑ",
	"ㅒ",
	"ㅓ",
	"ㅔ",
	"ㅕ",
	"ㅖ",
	"ㅗ",
	"ㅘ",
	"ㅙ",
	"ㅚ",
	"ㅛ",
	"ㅜ",
	"ㅝ",
	"ㅞ",
	"ㅟ",
	"ㅠ",
	"ㅡ",
	"ㅢ",
	"ㅣ",
)

TRAILING_COMPAT = (
	"",
	"ㄱ",
	"ㄲ",
	"ㄳ",
	"ㄴ",
	"ㄵ",
	"ㄶ",
	"ㄷ",
	"ㄹ",
	"ㄺ",
	"ㄻ",
	"ㄼ",
	"ㄽ",
	"ㄾ",
	"ㄿ",
	"ㅀ",
	"ㅁ",
	"ㅂ",
	"ㅄ",
	"ㅅ",
	"ㅆ",
	"ㅇ",
	"ㅈ",
	"ㅊ",
	"ㅋ",
	"ㅌ",
	"ㅍ",
	"ㅎ",
)

COMPLEX_COMPAT_MAP = {
	# Double consonants
	"ㄲ": "ㄱㄱ",
	"ㄸ": "ㄷㄷ",
	"ㅃ": "ㅂㅂ",
	"ㅆ": "ㅅㅅ",
	"ㅉ": "ㅈㅈ",
	# Complex vowels
	"ㅘ": "ㅗㅏ",
	"ㅙ": "ㅗㅐ",
	"ㅚ": "ㅗㅣ",
	"ㅝ": "ㅜㅓ",
	"ㅞ": "ㅜㅔ",
	"ㅟ": "ㅜㅣ",
	"ㅢ": "ㅡㅣ",
	# Final consonant clusters
	"ㄳ": "ㄱㅅ",
	"ㄵ": "ㄴㅈ",
	"ㄶ": "ㄴㅎ",
	"ㄺ": "ㄹㄱ",
	"ㄻ": "ㄹㅁ",
	"ㄼ": "ㄹㅂ",
	"ㄽ": "ㄹㅅ",
	"ㄾ": "ㄹㅌ",
	"ㄿ": "ㄹㅍ",
	"ㅀ": "ㄹㅎ",
	"ㅄ": "ㅂㅅ",
}

HANGUL_RANGES = (
	(0x1100, 0x11FF),  # Hangul Jamo
	(0x3130, 0x318F),  # Hangul Compatibility Jamo
	(0xA960, 0xA97F),  # Hangul Jamo Extended-A
	(0xAC00, 0xD7A3),  # Hangul Syllables
	(0xD7B0, 0xD7FF),  # Hangul Jamo Extended-B
)


@dataclass(frozen=True)
class SplitOptions:
	splitComplexLetters: bool = True
	insertSpacesBetweenLetters: bool = False


@dataclass(frozen=True)
class _Unit:
	text: str
	isWhitespace: bool
	isHangulLetter: bool


def _is_hangul_syllable(char: str) -> bool:
	scalar = ord(char)
	return S_BASE <= scalar <= S_END


def is_hangul_script_char(char: str) -> bool:
	scalar = ord(char)
	for start, end in HANGUL_RANGES:
		if start <= scalar <= end:
			return True
	return False


def keep_only_hangul(text: str, include_whitespace: bool = True) -> str:
	filtered_chars: list[str] = []
	for char in text:
		if is_hangul_script_char(char) or (include_whitespace and char.isspace()):
			filtered_chars.append(char)
	return "".join(filtered_chars)


def split_hangul_blocks(input_text: str, options: SplitOptions) -> str:
	if not input_text:
		return ""

	units: list[_Unit] = []
	for char in input_text:
		if not _is_hangul_syllable(char):
			units.append(_Unit(text=char, isWhitespace=char.isspace(), isHangulLetter=False))
			continue

		s_index = ord(char) - S_BASE
		l_index = s_index // N_COUNT
		v_index = (s_index % N_COUNT) // T_COUNT
		t_index = s_index % T_COUNT

		if not 0 <= l_index < L_COUNT:
			units.append(_Unit(text=char, isWhitespace=char.isspace(), isHangulLetter=False))
			continue

		units.append(_Unit(text=LEADING_COMPAT[l_index], isWhitespace=False, isHangulLetter=True))
		units.append(_Unit(text=VOWEL_COMPAT[v_index], isWhitespace=False, isHangulLetter=True))
		if t_index != 0:
			units.append(_Unit(text=TRAILING_COMPAT[t_index], isWhitespace=False, isHangulLetter=True))

	if options.splitComplexLetters:
		expanded: list[_Unit] = []
		for unit in units:
			if not unit.isHangulLetter or len(unit.text) != 1:
				expanded.append(unit)
				continue
			mapped = COMPLEX_COMPAT_MAP.get(unit.text)
			if not mapped:
				expanded.append(unit)
				continue
			for mapped_char in mapped:
				expanded.append(_Unit(text=mapped_char, isWhitespace=False, isHangulLetter=True))
		units = expanded

	if not options.insertSpacesBetweenLetters:
		return "".join(unit.text for unit in units)

	output_parts: list[str] = []
	previous_was_hangul_letter = False
	for unit in units:
		if unit.isWhitespace:
			output_parts.append(unit.text)
			previous_was_hangul_letter = False
			continue
		if unit.isHangulLetter and previous_was_hangul_letter:
			output_parts.append(" ")
		output_parts.append(unit.text)
		previous_was_hangul_letter = unit.isHangulLetter

	return "".join(output_parts)
