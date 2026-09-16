from __future__ import annotations

from dataclasses import dataclass
import gzip
import json
from pathlib import Path

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

HANJA_RANGES = (
	(0x3400, 0x4DBF),    # CJK Unified Ideographs Extension A
	(0x4E00, 0x9FFF),    # CJK Unified Ideographs
	(0xF900, 0xFAFF),    # CJK Compatibility Ideographs
	(0x20000, 0x2A6DF),  # Extension B
	(0x2A700, 0x2B73F),  # Extension C
	(0x2B740, 0x2B81F),  # Extension D
	(0x2B820, 0x2CEAF),  # Extension E
	(0x2CEB0, 0x2EBEF),  # Extension F
	(0x2F800, 0x2FA1F),  # CJK Compatibility Ideographs Supplement
)

PHONETIC_OFF = "off"
PHONETIC_SHORT = "short"
PHONETIC_FULL = "full"

# Standard Korean screen reader phonetic mnemonics
KOREAN_PHONETIC_MNEMONICS: dict[str, tuple[str, str]] = {
	# Consonants (초성/종성)
	"ㄱ": ("가을", "가을 기역"),
	"ㄲ": ("까치", "까치 쌍기역"),
	"ㄴ": ("나무", "나무 니은"),
	"ㄷ": ("다리", "다리 디귿"),
	"ㄸ": ("딸기", "딸기 쌍디귿"),
	"ㄹ": ("리본", "리본 리을"),
	"ㅁ": ("마루", "마루 미음"),
	"ㅂ": ("바람", "바람 비읍"),
	"ㅃ": ("빨래", "빨래 쌍비읍"),
	"ㅅ": ("소리", "소리 시옷"),
	"ㅆ": ("씨앗", "씨앗 쌍시옷"),
	"ㅇ": ("동글", "동글 이응"),
	"ㅈ": ("장미", "장미 지읒"),
	"ㅉ": ("짱구", "짱구 쌍지읒"),
	"ㅊ": ("차례", "차례 치읓"),
	"ㅋ": ("커피", "커피 키읔"),
	"ㅌ": ("토끼", "토끼 티읕"),
	"ㅍ": ("파도", "파도 피읍"),
	"ㅎ": ("하늘", "하늘 히흫"),

	# Vowels (중성)
	"ㅏ": ("아침", "아침 아"),
	"ㅐ": ("앵두", "앵두 애"),
	"ㅑ": ("야구", "야구 야"),
	"ㅒ": ("얘기", "얘기 얘"),
	"ㅓ": ("어부", "어부 어"),
	"ㅔ": ("에미", "에미 에"),
	"ㅕ": ("여름", "여름 여"),
	"ㅖ": ("옛날", "옛날 예"),
	"ㅗ": ("오리", "오리 오"),
	"ㅘ": ("왕자", "왕자 와"),
	"ㅙ": ("왜골", "왜골 왜"),
	"ㅚ": ("웨딩", "웨딩 외"),
	"ㅛ": ("요술", "요술 요"),
	"ㅜ": ("우물", "우물 우"),
	"ㅝ": ("원수", "원수 워"),
	"ㅞ": ("외출", "외출 웨"),
	"ㅟ": ("위치", "위치 위"),
	"ㅠ": ("유리", "유리 유"),
	"ㅡ": ("응달", "응달 으"),
	"ㅢ": ("의사", "의사 의"),
	"ㅣ": ("이름", "이름 이"),

	# Complex final consonants (used when splitComplexLetters=False)
	"ㄳ": ("기역시옷", "기역 시옷"),
	"ㄵ": ("니은지읒", "니은 지읒"),
	"ㄶ": ("니은히흫", "니은 히흫"),
	"ㄺ": ("리을기역", "리을 기역"),
	"ㄻ": ("리을미음", "리을 미음"),
	"ㄼ": ("리을비읍", "리을 비읍"),
	"ㄽ": ("리을시옷", "리을 시옷"),
	"ㄾ": ("리을티읕", "리을 티읕"),
	"ㄿ": ("리을피읍", "리을 피읍"),
	"ㅀ": ("리을히흫", "리을 히흫"),
	"ㅄ": ("비읍시옷", "비읍 시옷"),
}


@dataclass(frozen=True)
class SplitOptions:
	splitComplexLetters: bool = True
	insertSpacesBetweenLetters: bool = False
	phoneticMode: str = PHONETIC_OFF
	phoneticDescriptions: bool = False
	lookupHanja: bool = True


@dataclass(frozen=True)
class _Unit:
	text: str
	isWhitespace: bool
	isHangulLetter: bool
	isHanja: bool = False


def _is_hangul_syllable(char: str) -> bool:
	if not char:
		return False
	scalar = ord(char)
	return S_BASE <= scalar <= S_END


def is_hangul_script_char(char: str) -> bool:
	if not char:
		return False
	scalar = ord(char)
	for start, end in HANGUL_RANGES:
		if start <= scalar <= end:
			return True
	return False


def is_hanja_char(char: str) -> bool:
	if not char:
		return False
	scalar = ord(char)
	for start, end in HANJA_RANGES:
		if start <= scalar <= end:
			return True
	return False


def is_hangul_or_hanja_char(char: str) -> bool:
	return is_hangul_script_char(char) or is_hanja_char(char)


def keep_only_hangul(text: str, include_whitespace: bool = True) -> str:
	filtered_chars: list[str] = []
	for char in text:
		if is_hangul_script_char(char) or (include_whitespace and char.isspace()):
			filtered_chars.append(char)
	return "".join(filtered_chars)


def keep_only_hangul_and_hanja(text: str, include_whitespace: bool = True) -> str:
	filtered_chars: list[str] = []
	for char in text:
		if is_hangul_or_hanja_char(char) or (include_whitespace and char.isspace()):
			filtered_chars.append(char)
	return "".join(filtered_chars)


_HANJA_DB: dict[str, tuple[int, str, str]] | None = None


def _get_hanja_database() -> dict[str, tuple[int, str, str]]:
	global _HANJA_DB
	if _HANJA_DB is not None:
		return _HANJA_DB

	db: dict[str, tuple[int, str, str]] = {}
	data_path = Path(__file__).resolve().parent / "data" / "hanja.json.gz"
	if data_path.exists():
		try:
			with gzip.open(data_path, "rt", encoding="utf-8") as f:
				raw_data = json.load(f)
			for ch, val in raw_data.items():
				db[ch] = (int(val[0]), str(val[1]), str(val[2]))
			_HANJA_DB = db
			return _HANJA_DB
		except Exception:
			pass

	_HANJA_DB = db
	return _HANJA_DB


def lookup_hanja(char: str) -> tuple[int, str, str] | None:
	"""Looks up a Hanja character in the 27,786-entry database.
	Returns (stroke_count, eum, hoon_eum) or None.
	"""
	if not char or len(char) != 1:
		return None
	db = _get_hanja_database()
	return db.get(char)


def get_hanja_description(char: str) -> str | None:
	"""Returns the formatted description for a Hanja character,
	e.g. '집 가, 10획'.
	"""
	info = lookup_hanja(char)
	if not info:
		return None
	strokes, _eum, hoon_eum = info
	return f"{hoon_eum}, {strokes}획"


def split_hangul_blocks(input_text: str, options: SplitOptions) -> str:
	if not input_text:
		return ""

	phonetic_mode = options.phoneticMode
	if options.phoneticDescriptions and phonetic_mode == PHONETIC_OFF:
		phonetic_mode = PHONETIC_SHORT
	use_phonetic = phonetic_mode in (PHONETIC_SHORT, PHONETIC_FULL)

	units: list[_Unit] = []
	for char in input_text:
		if _is_hangul_syllable(char):
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
		elif options.lookupHanja and is_hanja_char(char):
			hanja_desc = get_hanja_description(char)
			if hanja_desc:
				units.append(_Unit(text=hanja_desc, isWhitespace=False, isHangulLetter=False, isHanja=True))
			else:
				units.append(_Unit(text=char, isWhitespace=False, isHangulLetter=False))
		elif is_hangul_script_char(char):
			units.append(_Unit(text=char, isWhitespace=False, isHangulLetter=True))
		else:
			units.append(_Unit(text=char, isWhitespace=char.isspace(), isHangulLetter=False))

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

	if use_phonetic:
		output_parts: list[str] = []
		for unit in units:
			if unit.isHangulLetter:
				mnemonic = KOREAN_PHONETIC_MNEMONICS.get(unit.text)
				if mnemonic:
					desc = mnemonic[0] if phonetic_mode == PHONETIC_SHORT else mnemonic[1]
				else:
					desc = unit.text
				if output_parts and not output_parts[-1].endswith((" ", "\n", "\t", ", ")):
					output_parts.append(", ")
				output_parts.append(desc)
			elif unit.isHanja:
				if output_parts and not output_parts[-1].endswith((" ", "\n", "\t", ", ")):
					output_parts.append(", ")
				output_parts.append(unit.text)
			else:
				output_parts.append(unit.text)
		return "".join(output_parts)

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


def decompose_for_review(text: str, options: SplitOptions) -> str:
	"""Formats character(s) under review cursor or caret for speech announcement.
	- If Hanja: returns stroke count and reading/meaning ('집 가, 10획').
	- If Hangul: decomposes into Jamo or phonetic mnemonics according to options.
	"""
	if not text:
		return ""

	# Check if phonetic mode is enabled
	phonetic_mode = options.phoneticMode
	if options.phoneticDescriptions and phonetic_mode == PHONETIC_OFF:
		phonetic_mode = PHONETIC_SHORT
	use_phonetic = phonetic_mode in (PHONETIC_SHORT, PHONETIC_FULL)

	if use_phonetic:
		return split_hangul_blocks(text, options)

	# In standard mode (phonetic off):
	parts: list[str] = []
	for ch in text:
		if is_hanja_char(ch):
			desc = get_hanja_description(ch)
			parts.append(desc if desc else ch)
		elif _is_hangul_syllable(ch):
			jamo_units = split_hangul_blocks(
				ch,
				SplitOptions(
					splitComplexLetters=options.splitComplexLetters,
					insertSpacesBetweenLetters=False,
					phoneticMode=PHONETIC_OFF,
					lookupHanja=False,
				),
			)
			parts.append(", ".join(jamo_units))
		elif is_hangul_script_char(ch):
			parts.append(ch)
		elif ch.isspace():
			continue
		else:
			parts.append(ch)

	return ", ".join(parts)
