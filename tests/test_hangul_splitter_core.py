from __future__ import annotations

from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CORE_DIR = PROJECT_ROOT / "addon" / "globalPlugins"
sys.path.insert(0, str(CORE_DIR))

from _hangulSplitterCore import (  # noqa: E402
	SplitOptions,
	is_hangul_script_char,
	keep_only_hangul,
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


if __name__ == "__main__":
	unittest.main()
