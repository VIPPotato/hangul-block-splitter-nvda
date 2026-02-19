from __future__ import annotations

from typing import Callable

import addonHandler
import api
import config
import globalPluginHandler
import gui
from gui import guiHelper
import languageHandler
from scriptHandler import getLastScriptRepeatCount, script
import speech
import textInfos
import treeInterceptorHandler
import ui
import wx

from ._hangulSplitterCore import SplitOptions, keep_only_hangul, split_hangul_blocks

addonHandler.initTranslation()


CONF_SECTION = "hangulBlockSplitter"
KEY_SPLIT_COMPLEX = "splitComplexLetters"
KEY_INSERT_SPACES = "insertSpacesBetweenLetters"
KEY_LIVE_UPDATE_IN_DIALOG = "liveUpdateInDialog"
KEY_DEFAULT_SOURCE_SCOPE = "defaultSourceScope"

SCOPE_CHARACTER = "character"
SCOPE_WORD = "word"
SCOPE_LINE = "line"
SCOPE_SELECTION = "selection"

_DEFAULT_SCOPE_VALUES = (SCOPE_CHARACTER, SCOPE_WORD, SCOPE_LINE)

CONF_SPEC = {
	KEY_SPLIT_COMPLEX: "boolean(default=True)",
	KEY_INSERT_SPACES: "boolean(default=False)",
	KEY_LIVE_UPDATE_IN_DIALOG: "boolean(default=True)",
	KEY_DEFAULT_SOURCE_SCOPE: "string(default=\"character\")",
}


def _is_korean_locale() -> bool:
	lang = languageHandler.getLanguage() or ""
	return lang.lower().startswith("ko")


def _tr(english: str, korean: str) -> str:
	return korean if _is_korean_locale() else _(english)


def _ensure_config_spec() -> None:
	if CONF_SECTION not in config.conf.spec:
		config.conf.spec[CONF_SECTION] = {}
	conf_spec = config.conf.spec[CONF_SECTION]
	for key, value in CONF_SPEC.items():
		if key not in conf_spec:
			conf_spec[key] = value


def _get_conf_section():
	_ensure_config_spec()
	return config.conf[CONF_SECTION]


def _get_split_options() -> SplitOptions:
	conf = _get_conf_section()
	return SplitOptions(
		splitComplexLetters=bool(conf[KEY_SPLIT_COMPLEX]),
		insertSpacesBetweenLetters=bool(conf[KEY_INSERT_SPACES]),
	)


def _save_split_options(options: SplitOptions) -> None:
	conf = _get_conf_section()
	conf[KEY_SPLIT_COMPLEX] = bool(options.splitComplexLetters)
	conf[KEY_INSERT_SPACES] = bool(options.insertSpacesBetweenLetters)


def _get_live_update_setting() -> bool:
	conf = _get_conf_section()
	return bool(conf[KEY_LIVE_UPDATE_IN_DIALOG])


def _save_live_update_setting(enabled: bool) -> None:
	conf = _get_conf_section()
	conf[KEY_LIVE_UPDATE_IN_DIALOG] = bool(enabled)


def _normalize_source_scope(scope: str) -> str:
	normalized = str(scope).strip().lower()
	if normalized in _DEFAULT_SCOPE_VALUES:
		return normalized
	return SCOPE_CHARACTER


def _get_default_source_scope() -> str:
	conf = _get_conf_section()
	return _normalize_source_scope(conf[KEY_DEFAULT_SOURCE_SCOPE])


def _save_default_source_scope(scope: str) -> None:
	conf = _get_conf_section()
	conf[KEY_DEFAULT_SOURCE_SCOPE] = _normalize_source_scope(scope)


def _get_default_source_scope_labels() -> dict[str, str]:
	return {
		SCOPE_CHARACTER: _tr("Single Hangul block under cursor", "커서 아래 한글 한 글자"),
		SCOPE_WORD: _tr("Current word under cursor", "커서가 있는 현재 단어"),
		SCOPE_LINE: _tr("Current line", "현재 줄"),
	}


def _scope_name_for_message(scope: str) -> str:
	labels = _get_default_source_scope_labels()
	return labels.get(_normalize_source_scope(scope), labels[SCOPE_CHARACTER])


def _get_text_container():
	obj = api.getFocusObject()
	tree_interceptor = getattr(obj, "treeInterceptor", None)
	if isinstance(tree_interceptor, treeInterceptorHandler.DocumentTreeInterceptor) and not tree_interceptor.passThrough:
		return tree_interceptor
	return obj


def _get_caret_text_info():
	obj = _get_text_container()
	try:
		return obj.makeTextInfo(textInfos.POSITION_CARET)
	except (AttributeError, NotImplementedError, RuntimeError):
		return None


def _get_selection_text() -> str:
	obj = _get_text_container()
	try:
		info = obj.makeTextInfo(textInfos.POSITION_SELECTION)
	except (AttributeError, NotImplementedError, RuntimeError):
		return ""
	if getattr(info, "isCollapsed", True):
		return ""
	return info.text or ""


def _get_current_line_text() -> str:
	info = _get_caret_text_info()
	if info is None:
		return ""
	try:
		line_info = info.copy()
		line_info.expand(textInfos.UNIT_LINE)
		return line_info.text or ""
	except (AttributeError, RuntimeError):
		return ""


def _get_current_word_text() -> str:
	info = _get_caret_text_info()
	if info is None:
		return ""
	try:
		word_info = info.copy()
		word_info.expand(textInfos.UNIT_WORD)
		return word_info.text or ""
	except (AttributeError, RuntimeError):
		return ""


def _extract_character_from_info(info) -> str:
	try:
		char_info = info.copy()
		char_info.expand(textInfos.UNIT_CHARACTER)
		text = char_info.text or ""
		if text:
			return text
		char_info = info.copy()
		moved = char_info.move(textInfos.UNIT_CHARACTER, -1)
		if moved:
			char_info.expand(textInfos.UNIT_CHARACTER)
			return char_info.text or ""
	except (AttributeError, RuntimeError):
		return ""
	return ""


def _get_character_under_cursor() -> str:
	caret_info = _get_caret_text_info()
	if caret_info is not None:
		text = _extract_character_from_info(caret_info)
		if text:
			return text
	try:
		review_info = api.getReviewPosition().copy()
		review_info.expand(textInfos.UNIT_CHARACTER)
		return review_info.text or ""
	except (AttributeError, RuntimeError):
		return ""


def _get_text_from_scope(scope: str) -> tuple[str, str]:
	normalized_scope = _normalize_source_scope(scope)
	if normalized_scope == SCOPE_LINE:
		return _get_current_line_text(), SCOPE_LINE
	if normalized_scope == SCOPE_WORD:
		return _get_current_word_text(), SCOPE_WORD
	return _get_character_under_cursor(), SCOPE_CHARACTER


def _has_hangul_content(text: str) -> bool:
	return any(not char.isspace() for char in keep_only_hangul(text, include_whitespace=False))


def _sanitize_for_split(text: str) -> str:
	return keep_only_hangul(text, include_whitespace=True)


def _get_split_source_text(scope: str | None = None) -> tuple[str, str]:
	selection_text = _get_selection_text()
	if selection_text:
		return selection_text, SCOPE_SELECTION
	return _get_text_from_scope(scope or _get_default_source_scope())


def _get_dialog_seed_text() -> str:
	source_text, _source_kind = _get_split_source_text()
	sanitized_text = _sanitize_for_split(source_text)
	if _has_hangul_content(sanitized_text):
		return sanitized_text
	return ""


class HangulSplitterSettingsPanel(gui.settingsDialogs.SettingsPanel):
	title = _tr("Hangul Block Splitter", "한글 블록 분해기")

	def makeSettings(self, settingsSizer: wx.BoxSizer) -> None:
		helper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		conf = _get_conf_section()
		scope_labels = _get_default_source_scope_labels()
		self._default_scope_values = list(_DEFAULT_SCOPE_VALUES)

		self._split_complex_checkbox = helper.addItem(
			wx.CheckBox(
				self,
				label=_tr(
					"Split complex letters by default (ㅘ -> ㅗㅏ, ㄳ -> ㄱㅅ, ㅄ -> ㅂㅅ)",
					"겹모음/겹받침을 기본으로 더 잘게 분해하기 (ㅘ -> ㅗㅏ, ㄳ -> ㄱㅅ, ㅄ -> ㅂㅅ)",
				),
			),
		)
		self._split_complex_checkbox.SetValue(bool(conf[KEY_SPLIT_COMPLEX]))

		self._insert_spaces_checkbox = helper.addItem(
			wx.CheckBox(
				self,
				label=_tr(
					"Insert spaces between Hangul letters by default",
					"분해된 한글 글자 사이에 공백을 기본으로 넣기",
				),
			),
		)
		self._insert_spaces_checkbox.SetValue(bool(conf[KEY_INSERT_SPACES]))

		self._live_update_checkbox = helper.addItem(
			wx.CheckBox(
				self,
				label=_tr(
					"Update splitter dialog output while typing",
					"입력할 때 분해 결과를 실시간으로 갱신하기",
				),
			),
		)
		self._live_update_checkbox.SetValue(bool(conf[KEY_LIVE_UPDATE_IN_DIALOG]))

		self._default_scope_choice = helper.addLabeledControl(
			_tr(
				"When no text is selected, split this range:",
				"텍스트를 선택하지 않았을 때 분해할 범위:",
			),
			wx.Choice,
			choices=[scope_labels[scope] for scope in self._default_scope_values],
		)
		current_scope = _get_default_source_scope()
		try:
			selected_index = self._default_scope_values.index(current_scope)
		except ValueError:
			selected_index = 0
		self._default_scope_choice.SetSelection(selected_index)

	def onSave(self) -> None:
		conf = _get_conf_section()
		conf[KEY_SPLIT_COMPLEX] = self._split_complex_checkbox.GetValue()
		conf[KEY_INSERT_SPACES] = self._insert_spaces_checkbox.GetValue()
		conf[KEY_LIVE_UPDATE_IN_DIALOG] = self._live_update_checkbox.GetValue()
		selected_index = self._default_scope_choice.GetSelection()
		if selected_index < 0:
			selected_scope = SCOPE_CHARACTER
		else:
			selected_scope = self._default_scope_values[selected_index]
		_save_default_source_scope(selected_scope)


class HangulSplitterDialog(wx.Dialog):
	def __init__(
		self,
		parent: wx.Window | None,
		initial_text: str,
		on_close: Callable[[], None],
	):
		super().__init__(parent=parent, title=_tr("Hangul Block Splitter", "한글 블록 분해기"))
		self._on_close = on_close
		self._closed = False
		self._normalizing_input = False
		self._build_ui(initial_text)
		self.Bind(wx.EVT_CLOSE, self._on_close_event)

	def _build_ui(self, initial_text: str) -> None:
		main_sizer = wx.BoxSizer(wx.VERTICAL)

		input_label = wx.StaticText(self, label=_tr("Input text", "입력 텍스트"))
		self._input_edit = wx.TextCtrl(self, style=wx.TE_MULTILINE)
		self._input_edit.SetValue(initial_text)

		options_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, _tr("Options", "옵션"))
		self._split_complex_checkbox = wx.CheckBox(
			self,
			label=_tr(
				"Split complex letters (ㅘ -> ㅗㅏ, ㄳ -> ㄱㅅ, ㅄ -> ㅂㅅ)",
				"겹모음/겹받침 분해하기 (ㅘ -> ㅗㅏ, ㄳ -> ㄱㅅ, ㅄ -> ㅂㅅ)",
			),
		)
		self._insert_spaces_checkbox = wx.CheckBox(
			self,
			label=_tr("Insert spaces between letters", "글자 사이에 공백 넣기"),
		)
		self._live_update_checkbox = wx.CheckBox(
			self,
			label=_tr("Update output as you type", "입력할 때 결과 바로 갱신"),
		)
		conf = _get_conf_section()
		self._split_complex_checkbox.SetValue(bool(conf[KEY_SPLIT_COMPLEX]))
		self._insert_spaces_checkbox.SetValue(bool(conf[KEY_INSERT_SPACES]))
		self._live_update_checkbox.SetValue(bool(conf[KEY_LIVE_UPDATE_IN_DIALOG]))
		options_sizer.Add(self._split_complex_checkbox, border=2, flag=wx.BOTTOM)
		options_sizer.Add(self._insert_spaces_checkbox, border=2, flag=wx.BOTTOM)
		options_sizer.Add(self._live_update_checkbox)

		output_label = wx.StaticText(
			self,
			label=_tr("Output text (read-only)", "결과 텍스트(읽기 전용)"),
		)
		self._output_edit = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)

		button_row = wx.BoxSizer(wx.HORIZONTAL)
		self._split_button = wx.Button(self, label=_tr("&Split", "&분해"))
		self._copy_button = wx.Button(self, label=_tr("&Copy output", "결과 &복사"))
		self._clear_button = wx.Button(self, label=_tr("C&lear", "&지우기"))
		close_button = wx.Button(self, wx.ID_CANCEL, _tr("&Close", "&닫기"))
		button_row.Add(self._split_button, border=5, flag=wx.RIGHT)
		button_row.Add(self._copy_button, border=5, flag=wx.RIGHT)
		button_row.Add(self._clear_button, border=5, flag=wx.RIGHT)
		button_row.Add(close_button)

		self._status_label = wx.StaticText(self, label=_tr("Ready.", "준비됨."))

		main_sizer.Add(input_label, border=6, flag=wx.LEFT | wx.TOP)
		main_sizer.Add(self._input_edit, proportion=1, border=6, flag=wx.EXPAND | wx.LEFT | wx.RIGHT)
		main_sizer.Add(options_sizer, border=6, flag=wx.EXPAND | wx.ALL)
		main_sizer.Add(output_label, border=6, flag=wx.LEFT)
		main_sizer.Add(
			self._output_edit,
			proportion=1,
			border=6,
			flag=wx.EXPAND | wx.LEFT | wx.RIGHT,
		)
		main_sizer.Add(button_row, border=6, flag=wx.LEFT | wx.RIGHT | wx.TOP)
		main_sizer.Add(self._status_label, border=6, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM)

		self.SetSizer(main_sizer)
		self.SetMinSize((640, 460))
		self.SetSize((760, 560))

		self._split_button.Bind(wx.EVT_BUTTON, self._on_split)
		self._copy_button.Bind(wx.EVT_BUTTON, self._on_copy_output)
		self._clear_button.Bind(wx.EVT_BUTTON, self._on_clear)
		close_button.Bind(wx.EVT_BUTTON, lambda evt: self.Close())
		self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)
		self._input_edit.Bind(wx.EVT_TEXT, self._on_input_text_change)
		self._split_complex_checkbox.Bind(wx.EVT_CHECKBOX, self._on_live_update_change)
		self._insert_spaces_checkbox.Bind(wx.EVT_CHECKBOX, self._on_live_update_change)
		self._live_update_checkbox.Bind(wx.EVT_CHECKBOX, self._on_live_update_toggle)
		self.SetEscapeId(wx.ID_CANCEL)

		self._enforce_hangul_input()
		self._update_output(announce=False)
		wx.CallAfter(self._input_edit.SetFocus)

	def _current_options(self) -> SplitOptions:
		return SplitOptions(
			splitComplexLetters=self._split_complex_checkbox.GetValue(),
			insertSpacesBetweenLetters=self._insert_spaces_checkbox.GetValue(),
		)

	def _save_preferences(self) -> None:
		_save_split_options(self._current_options())
		_save_live_update_setting(self._live_update_checkbox.GetValue())

	def get_input_text(self) -> str:
		return self._input_edit.GetValue()

	def set_input_text(self, text: str) -> None:
		self._input_edit.SetValue(_sanitize_for_split(text))
		self._update_output(announce=False)

	def _enforce_hangul_input(self) -> bool:
		current_text = self._input_edit.GetValue()
		filtered_text = _sanitize_for_split(current_text)
		if filtered_text == current_text:
			return False
		cursor_pos = self._input_edit.GetInsertionPoint()
		self._normalizing_input = True
		self._input_edit.ChangeValue(filtered_text)
		self._input_edit.SetInsertionPoint(min(cursor_pos, len(filtered_text)))
		self._normalizing_input = False
		return True

	def _set_status(self, text: str) -> None:
		self._status_label.SetLabel(text)

	def _update_output(self, announce: bool) -> None:
		output = split_hangul_blocks(self._input_edit.GetValue(), self._current_options())
		self._output_edit.ChangeValue(output)
		if announce:
			self._set_status(_tr("Output updated.", "결과를 갱신했습니다."))

	def _on_split(self, evt: wx.CommandEvent) -> None:
		self._update_output(announce=True)

	def _on_copy_output(self, evt: wx.CommandEvent) -> None:
		text = self._output_edit.GetValue()
		if not text:
			self._set_status(_tr("Nothing to copy.", "복사할 내용이 없습니다."))
			ui.message(_tr("Nothing to copy.", "복사할 내용이 없습니다."))
			return
		if api.copyToClip(text, notify=True):
			self._set_status(_tr("Output copied to clipboard.", "결과를 클립보드에 복사했습니다."))
		else:
			self._set_status(_tr("Unable to copy output.", "결과를 복사하지 못했습니다."))

	def _on_clear(self, evt: wx.CommandEvent) -> None:
		self._input_edit.Clear()
		self._output_edit.Clear()
		self._input_edit.SetFocus()
		self._set_status(_tr("Cleared.", "입력과 결과를 지웠습니다."))

	def _on_live_update_toggle(self, evt: wx.CommandEvent) -> None:
		if self._live_update_checkbox.GetValue():
			self._update_output(announce=False)
			self._set_status(_tr("Live update is on.", "실시간 갱신이 켜졌습니다."))
		else:
			self._set_status(
				_tr(
					"Live update is off. Press Split to refresh output.",
					"실시간 갱신이 꺼졌습니다. 분해 버튼을 눌러 결과를 갱신하세요.",
				),
			)

	def _on_live_update_change(self, evt: wx.CommandEvent) -> None:
		if self._live_update_checkbox.GetValue():
			self._update_output(announce=False)
		evt.Skip()

	def _on_input_text_change(self, evt: wx.CommandEvent) -> None:
		if self._normalizing_input:
			evt.Skip()
			return
		if self._enforce_hangul_input():
			self._set_status(
				_tr(
					"Only Hangul characters are accepted. Non-Hangul input was ignored.",
					"한글만 입력할 수 있습니다. 한글이 아닌 문자는 자동으로 제외했습니다.",
				),
			)
		if self._live_update_checkbox.GetValue():
			self._update_output(announce=False)
		evt.Skip()

	def _on_char_hook(self, evt: wx.KeyEvent) -> None:
		if evt.GetKeyCode() == wx.WXK_ESCAPE:
			self.Close()
			return
		evt.Skip()

	def _on_close_event(self, evt: wx.CloseEvent) -> None:
		if self._closed:
			evt.Skip()
			return
		self._closed = True
		self._save_preferences()
		try:
			self._on_close()
		finally:
			self.Destroy()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = _tr("Hangul Block Splitter", "한글 블록 분해기")

	def __init__(self):
		super().__init__()
		_ensure_config_spec()
		self._dialog: HangulSplitterDialog | None = None
		self._tools_menu_item: wx.MenuItem | None = None
		self._register_settings_panel()
		self._add_tools_menu_item()

	def terminate(self):
		if self._dialog:
			dialog = self._dialog
			self._dialog = None
			try:
				if dialog:
					wx.CallAfter(dialog.Close)
			except RuntimeError:
				pass
		self._remove_tools_menu_item()
		self._unregister_settings_panel()
		super().terminate()

	def _add_tools_menu_item(self) -> None:
		main_frame = gui.mainFrame
		if not main_frame:
			return
		sys_tray_icon = getattr(main_frame, "sysTrayIcon", None)
		if not sys_tray_icon:
			return
		tools_menu = getattr(sys_tray_icon, "toolsMenu", None)
		if not tools_menu:
			return
		self._tools_menu_item = tools_menu.Append(
			wx.ID_ANY,
			_tr("Hangul Block Splitter...", "한글 블록 분해기(&H)..."),
		)
		sys_tray_icon.Bind(wx.EVT_MENU, self._on_tools_menu_item, self._tools_menu_item)

	def _remove_tools_menu_item(self) -> None:
		if not self._tools_menu_item:
			return
		main_frame = gui.mainFrame
		if not main_frame:
			self._tools_menu_item = None
			return
		sys_tray_icon = getattr(main_frame, "sysTrayIcon", None)
		if not sys_tray_icon:
			self._tools_menu_item = None
			return
		tools_menu = getattr(sys_tray_icon, "toolsMenu", None)
		if not tools_menu:
			self._tools_menu_item = None
			return
		try:
			sys_tray_icon.Unbind(wx.EVT_MENU, handler=self._on_tools_menu_item, source=self._tools_menu_item)
		except TypeError:
			sys_tray_icon.Unbind(wx.EVT_MENU, handler=self._on_tools_menu_item)
		try:
			tools_menu.Remove(self._tools_menu_item.GetId())
		except Exception:
			pass
		self._tools_menu_item = None

	def _on_tools_menu_item(self, evt: wx.CommandEvent) -> None:
		wx.CallAfter(self._show_dialog, _get_dialog_seed_text())

	def _register_settings_panel(self) -> None:
		categories = gui.settingsDialogs.NVDASettingsDialog.categoryClasses
		if HangulSplitterSettingsPanel not in categories:
			categories.append(HangulSplitterSettingsPanel)

	def _unregister_settings_panel(self) -> None:
		categories = gui.settingsDialogs.NVDASettingsDialog.categoryClasses
		while HangulSplitterSettingsPanel in categories:
			categories.remove(HangulSplitterSettingsPanel)

	def _on_dialog_closed(self) -> None:
		self._dialog = None

	def _show_dialog(self, initial_text: str) -> None:
		if self._dialog:
			if initial_text and not self._dialog.get_input_text():
				self._dialog.set_input_text(initial_text)
			self._dialog.Raise()
			self._dialog.SetFocus()
			return
		self._dialog = HangulSplitterDialog(
			parent=gui.mainFrame,
			initial_text=initial_text,
			on_close=self._on_dialog_closed,
		)
		self._dialog.Show()
		self._dialog.Raise()

	def _get_split_result_from_context(self) -> tuple[str, str]:
		source_text, source_kind = _get_split_source_text()
		if not source_text:
			return "", source_kind
		sanitized_text = _sanitize_for_split(source_text)
		if not _has_hangul_content(sanitized_text):
			return "", source_kind
		return split_hangul_blocks(sanitized_text, _get_split_options()), source_kind

	def _announce_no_hangul_source(self, source_kind: str) -> None:
		if source_kind == SCOPE_SELECTION:
			ui.message(
				_tr(
					"Selected text does not contain Hangul.",
					"선택한 텍스트에 한글이 없습니다.",
				),
			)
			return
		if source_kind == SCOPE_LINE:
			ui.message(
				_tr(
					"The current line does not contain Hangul.",
					"현재 줄에 한글이 없습니다.",
				),
			)
			return
		if source_kind == SCOPE_WORD:
			ui.message(
				_tr(
					"The current word does not contain Hangul.",
					"현재 단어에 한글이 없습니다.",
				),
			)
			return
		ui.message(
			_tr(
				"No Hangul character under cursor.",
				"커서 아래 한글 문자를 찾을 수 없습니다.",
			),
		)

	@script(
		description=_tr(
			"Opens the Hangul splitter dialog with selected text, or the configured default range under cursor.",
			"선택한 텍스트 또는 설정한 기본 범위(한 글자/단어/줄)의 텍스트로 한글 분해기 대화상자를 엽니다.",
		),
		gesture="kb:NVDA+shift+h",
		speakOnDemand=True,
	)
	def script_openHangulSplitterDialog(self, gesture):
		wx.CallAfter(self._show_dialog, _get_dialog_seed_text())

	@script(
		description=_tr(
			"Describes each character of split selected Hangul text, or the configured default range under cursor. Press twice to copy the split result to clipboard.",
			"선택한 한글(없으면 설정한 기본 범위의 텍스트)을 분해한 뒤 각 글자를 문자 설명으로 읽어줍니다. 두 번 누르면 분해 결과를 클립보드에 복사합니다.",
		),
		gesture="kb:NVDA+alt+h",
		speakOnDemand=True,
	)
	def script_describeSplitHangul(self, gesture):
		result, source_kind = self._get_split_result_from_context()
		if not result:
			self._announce_no_hangul_source(source_kind)
			return
		repeat_count = getLastScriptRepeatCount()
		if repeat_count == 0:
			speech.speakSpelling(result, useCharacterDescriptions=True)
			return
		if not api.copyToClip(result, notify=True):
			ui.message(_tr("Unable to copy split result.", "분해 결과를 복사하지 못했습니다."))

	@script(
		description=_tr(
			"Copies split selected Hangul text, or the configured default range under cursor, to the clipboard.",
			"선택한 한글(선택이 없으면 설정한 기본 범위)을 분해해 클립보드에 복사합니다.",
		),
		speakOnDemand=True,
	)
	def script_copySplitHangulUnderCursor(self, gesture):
		result, source_kind = self._get_split_result_from_context()
		if not result:
			self._announce_no_hangul_source(source_kind)
			return
		if not api.copyToClip(result, notify=True):
			ui.message(_tr("Unable to copy split result.", "분해 결과를 복사하지 못했습니다."))

	@script(
		description=_tr(
			"Toggles splitting of complex Hangul letters for this add-on.",
			"이 추가 기능의 겹글자 분해를 켜거나 끕니다.",
		),
		speakOnDemand=True,
	)
	def script_toggleComplexLetterSplitting(self, gesture):
		conf = _get_conf_section()
		new_value = not bool(conf[KEY_SPLIT_COMPLEX])
		conf[KEY_SPLIT_COMPLEX] = new_value
		ui.message(
			_tr("Split complex letters on.", "겹글자 분해 켜짐.")
			if new_value
			else _tr("Split complex letters off.", "겹글자 분해 꺼짐."),
		)

	@script(
		description=_tr(
			"Toggles insertion of spaces between split Hangul letters for this add-on.",
			"이 추가 기능의 글자 사이 공백 삽입을 켜거나 끕니다.",
		),
		speakOnDemand=True,
	)
	def script_toggleInsertSpaces(self, gesture):
		conf = _get_conf_section()
		new_value = not bool(conf[KEY_INSERT_SPACES])
		conf[KEY_INSERT_SPACES] = new_value
		ui.message(
			_tr("Insert spaces on.", "공백 삽입 켜짐.")
			if new_value
			else _tr("Insert spaces off.", "공백 삽입 꺼짐."),
		)

	@script(
		description=_tr(
			"Toggles live update in the Hangul splitter dialog.",
			"한글 분해기 대화상자의 실시간 갱신을 켜거나 끕니다.",
		),
		speakOnDemand=True,
	)
	def script_toggleDialogLiveUpdate(self, gesture):
		new_value = not _get_live_update_setting()
		_save_live_update_setting(new_value)
		ui.message(
			_tr("Live update in dialog on.", "대화상자 실시간 갱신 켜짐.")
			if new_value
			else _tr("Live update in dialog off.", "대화상자 실시간 갱신 꺼짐."),
		)

	@script(
		description=_tr(
			"Cycles the default split range used when no text is selected.",
			"텍스트를 선택하지 않았을 때 사용할 기본 분해 범위를 순환 전환합니다.",
		),
		gesture="kb:NVDA+ctrl+h",
		speakOnDemand=True,
	)
	def script_cycleDefaultSourceScope(self, gesture):
		current_scope = _get_default_source_scope()
		try:
			current_index = _DEFAULT_SCOPE_VALUES.index(current_scope)
		except ValueError:
			current_index = 0
		next_scope = _DEFAULT_SCOPE_VALUES[(current_index + 1) % len(_DEFAULT_SCOPE_VALUES)]
		_save_default_source_scope(next_scope)
		ui.message(_scope_name_for_message(next_scope))
