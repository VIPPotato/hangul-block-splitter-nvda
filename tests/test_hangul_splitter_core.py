from __future__ import annotations

from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CORE_DIR = PROJECT_ROOT / "addon" / "globalPlugins"
sys.path.insert(0, str(CORE_DIR))

from _hangulSplitterCore import (  # noqa: E402
	PHONETIC_FULL,
	PHONETIC_OFF,
	PHONETIC_SHORT,
	SplitOptions,
	decompose_for_review,
	get_hanja_description,
	is_hangul_or_hanja_char,
	is_hangul_script_char,
	is_hanja_char,
	keep_only_hangul,
	keep_only_hangul_and_hanja,
	lookup_hanja,
	split_hangul_blocks,
)


class HangulSplitterCoreTests(unittest.TestCase):
	def test_simple_syllable(self) -> None:
		self.assertEqual(split_hangul_blocks("한", SplitOptions()), "ㅎㅏㄴ")

	def test_non_hangul_is_unchanged(self) -> None:
		self.assertEqual(split_hangul_blocks("ABC 123", SplitOptions()), "ABC 123")

	def test_complex_letters_enabled(self) -> None:
		options = SplitOptions(splitComplexLetters=True, insertSpacesBetweenLetters=False)
		self.assertEqual(split_hangul_blocks("괜", options), "ㄱㅗㅐㄴ")
		self.assertEqual(split_hangul_blocks("값", options), "ㄱㅏㅂㅅ")

	def test_complex_letters_disabled(self) -> None:
		options = SplitOptions(splitComplexLetters=False, insertSpacesBetweenLetters=False)
		self.assertEqual(split_hangul_blocks("괜", options), "ㄱㅙㄴ")
		self.assertEqual(split_hangul_blocks("값", options), "ㄱㅏㅄ")

	def test_insert_spaces(self) -> None:
		options = SplitOptions(splitComplexLetters=False, insertSpacesBetweenLetters=True)
		self.assertEqual(split_hangul_blocks("한글 테스트", options), "ㅎ ㅏ ㄴ ㄱ ㅡ ㄹ ㅌ ㅔ ㅅ ㅡ ㅌ ㅡ")

	def test_keep_only_hangul_filters_non_hangul(self) -> None:
		self.assertEqual(keep_only_hangul("abc한글!? 123"), "한글 ")
		self.assertEqual(keep_only_hangul("a한 b글", include_whitespace=False), "한글")

	def test_is_hangul_script_char(self) -> None:
		self.assertTrue(is_hangul_script_char("한"))
		self.assertTrue(is_hangul_script_char("ㄱ"))
		self.assertFalse(is_hangul_script_char("A"))

	def test_phonetic_short_mode(self) -> None:
		options = SplitOptions(phoneticMode=PHONETIC_SHORT)
		self.assertEqual(split_hangul_blocks("한", options), "하늘, 아침, 나무")

	def test_phonetic_full_mode(self) -> None:
		options = SplitOptions(phoneticMode=PHONETIC_FULL)
		self.assertEqual(split_hangul_blocks("한", options), "하늘 히흫, 아침 아, 나무 니은")

	def test_phonetic_descriptions_flag(self) -> None:
		options = SplitOptions(phoneticDescriptions=True)
		self.assertEqual(split_hangul_blocks("한", options), "하늘, 아침, 나무")

	def test_phonetic_complex_letters(self) -> None:
		options_split = SplitOptions(splitComplexLetters=True, phoneticMode=PHONETIC_SHORT)
		self.assertEqual(split_hangul_blocks("값", options_split), "가을, 아침, 바람, 소리")

		options_unsplit = SplitOptions(splitComplexLetters=False, phoneticMode=PHONETIC_SHORT)
		self.assertEqual(split_hangul_blocks("값", options_unsplit), "가을, 아침, 비읍시옷")

	def test_hanja_detection(self) -> None:
		self.assertTrue(is_hanja_char("家"))
		self.assertTrue(is_hanja_char("韓"))
		self.assertTrue(is_hanja_char("國"))
		self.assertFalse(is_hanja_char("한"))
		self.assertFalse(is_hanja_char("A"))

	def test_hanja_lookup(self) -> None:
		res = lookup_hanja("家")
		self.assertIsNotNone(res)
		strokes, eum, hoon_eum = res
		self.assertEqual(strokes, 10)
		self.assertEqual(eum, "가")
		self.assertEqual(hoon_eum, "집 가")

	def test_hanja_description(self) -> None:
		self.assertEqual(get_hanja_description("家"), "집 가, 10획")
		self.assertEqual(get_hanja_description("韓"), "한나라 한, 17획")
		self.assertEqual(get_hanja_description("國"), "나라 국, 11획")

	def test_is_hangul_or_hanja(self) -> None:
		self.assertTrue(is_hangul_or_hanja_char("한"))
		self.assertTrue(is_hangul_or_hanja_char("家"))
		self.assertFalse(is_hangul_or_hanja_char("1"))
		self.assertFalse(is_hangul_or_hanja_char("A"))

	def test_keep_only_hangul_and_hanja(self) -> None:
		self.assertEqual(keep_only_hangul_and_hanja("abc한글 家國!? 123"), "한글 家國 ")

	def test_split_hangul_with_hanja(self) -> None:
		options = SplitOptions(lookupHanja=True)
		self.assertEqual(split_hangul_blocks("家", options), "집 가, 10획")

	def test_decompose_for_review_hangul(self) -> None:
		# Standard mode gives comma-separated jamo for clear speech
		self.assertEqual(decompose_for_review("한", SplitOptions()), "ㅎ, ㅏ, ㄴ")
		# Phonetic mode
		self.assertEqual(
			decompose_for_review("한", SplitOptions(phoneticMode=PHONETIC_SHORT)),
			"하늘, 아침, 나무",
		)
		self.assertEqual(
			decompose_for_review("한", SplitOptions(phoneticMode=PHONETIC_FULL)),
			"하늘 히흫, 아침 아, 나무 니은",
		)

	def test_decompose_for_review_hanja(self) -> None:
		self.assertEqual(decompose_for_review("家", SplitOptions()), "집 가, 10획")
		self.assertEqual(decompose_for_review("韓國", SplitOptions()), "한나라 한, 17획, 나라 국, 11획")


if __name__ == "__main__":
	unittest.main()
