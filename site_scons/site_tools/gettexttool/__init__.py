"""This tool allows generation of gettext .mo compiled files, pot files from source code files
and pot files for merging.

Three new builders are added into the constructed environment:

- gettextMoFile: generates .mo file from .pot file using msgfmt.
- gettextPotFile: Generates .pot file from source code files.
- gettextMergePotFile: Creates a .pot file appropriate for merging into existing .po files.

To properly configure get text, define the following variables:

- gettext_package_bugs_address
- gettext_package_name
- gettext_package_version


"""

import ast
import struct

from SCons.Action import Action


def exists(env):
	return True


def _finalize_message(
	messages: dict[str, str],
	*,
	msgctxt: str | None,
	msgid: str,
	msgstr: str,
	fuzzy: bool,
) -> None:
	if fuzzy:
		return
	if msgid == "":
		# Keep the header message only when it has actual content.
		if not msgstr:
			return
		key = msgid if msgctxt is None else f"{msgctxt}\x04{msgid}"
		messages[key] = msgstr
		return
	if not msgstr:
		return
	key = msgid if msgctxt is None else f"{msgctxt}\x04{msgid}"
	messages[key] = msgstr


def _parse_po_file(po_path: str) -> dict[str, str]:
	messages: dict[str, str] = {}
	section: str | None = None
	msgctxt: str | None = None
	msgid = ""
	msgstr = ""
	fuzzy = False

	with open(po_path, "r", encoding="utf-8") as po_file:
		for line in po_file:
			line = line.rstrip("\n")
			stripped = line.strip()

			if not stripped:
				_finalize_message(
					messages,
					msgctxt=msgctxt,
					msgid=msgid,
					msgstr=msgstr,
					fuzzy=fuzzy,
				)
				section = None
				msgctxt = None
				msgid = ""
				msgstr = ""
				fuzzy = False
				continue

			if stripped.startswith("#,") and "fuzzy" in stripped:
				fuzzy = True
				continue
			if stripped.startswith("#"):
				continue

			if stripped.startswith("msgctxt "):
				section = "msgctxt"
				msgctxt = ast.literal_eval(stripped[7:].strip())
				continue
			if stripped.startswith("msgid_plural "):
				section = "msgid"
				msgid += "\x00" + ast.literal_eval(stripped[12:].strip())
				continue
			if stripped.startswith("msgid "):
				_finalize_message(
					messages,
					msgctxt=msgctxt,
					msgid=msgid,
					msgstr=msgstr,
					fuzzy=fuzzy,
				)
				section = "msgid"
				msgid = ast.literal_eval(stripped[5:].strip())
				msgstr = ""
				fuzzy = False
				continue
			if stripped.startswith("msgstr["):
				section = "msgstr"
				payload = stripped.split("]", 1)[1].strip()
				chunk = ast.literal_eval(payload)
				if msgstr:
					msgstr += "\x00"
				msgstr += chunk
				continue
			if stripped.startswith("msgstr "):
				section = "msgstr"
				msgstr = ast.literal_eval(stripped[6:].strip())
				continue
			if stripped.startswith('"'):
				chunk = ast.literal_eval(stripped)
				if section == "msgctxt":
					msgctxt = (msgctxt or "") + chunk
				elif section == "msgid":
					msgid += chunk
				elif section == "msgstr":
					msgstr += chunk
				continue

	_finalize_message(
		messages,
		msgctxt=msgctxt,
		msgid=msgid,
		msgstr=msgstr,
		fuzzy=fuzzy,
	)
	return messages


def _write_mo_file(messages: dict[str, str], mo_path: str) -> None:
	keys_blob = b""
	vals_blob = b""
	offsets: list[tuple[int, int, int, int]] = []
	for key in sorted(messages):
		key_data = key.encode("utf-8")
		val_data = messages[key].encode("utf-8")
		offsets.append((len(key_data), len(keys_blob), len(val_data), len(vals_blob)))
		keys_blob += key_data + b"\x00"
		vals_blob += val_data + b"\x00"

	count = len(offsets)
	ids_table_offset = 7 * 4
	strs_table_offset = ids_table_offset + count * 8
	keys_offset = strs_table_offset + count * 8
	vals_offset = keys_offset + len(keys_blob)

	with open(mo_path, "wb") as mo_file:
		mo_file.write(
			struct.pack(
				"<Iiiiiii",
				0x950412DE,
				0,
				count,
				ids_table_offset,
				strs_table_offset,
				0,
				0,
			),
		)
		for key_len, key_pos, _, _ in offsets:
			mo_file.write(struct.pack("<ii", key_len, keys_offset + key_pos))
		for _, _, val_len, val_pos in offsets:
			mo_file.write(struct.pack("<ii", val_len, vals_offset + val_pos))
		mo_file.write(keys_blob)
		mo_file.write(vals_blob)


def _compile_mo_with_python(target, source, env):
	po_path = str(source[0])
	mo_path = str(target[0])
	messages = _parse_po_file(po_path)
	_write_mo_file(messages, mo_path)
	return 0


XGETTEXT_COMMON_ARGS = (
	"--msgid-bugs-address='$gettext_package_bugs_address' "
	"--package-name='$gettext_package_name' "
	"--package-version='$gettext_package_version' "
	"--keyword=pgettext:1c,2 "
	"-c -o $TARGET $SOURCES"
)


def generate(env):
	env.SetDefault(gettext_package_bugs_address="example@example.com")
	env.SetDefault(gettext_package_name="")
	env.SetDefault(gettext_package_version="")

	msgfmt_cmd = env.WhereIs("msgfmt")
	if msgfmt_cmd:
		mo_action = Action("msgfmt -o $TARGET $SOURCE", "Compiling translation $SOURCE")
	else:
		mo_action = Action(
			_compile_mo_with_python,
			"Compiling translation $SOURCE (python fallback, msgfmt not found)",
		)

	env["BUILDERS"]["gettextMoFile"] = env.Builder(
		action=mo_action,
		suffix=".mo",
		src_suffix=".po",
	)

	env["BUILDERS"]["gettextPotFile"] = env.Builder(
		action=Action("xgettext " + XGETTEXT_COMMON_ARGS, "Generating pot file $TARGET"), suffix=".pot"
	)

	env["BUILDERS"]["gettextMergePotFile"] = env.Builder(
		action=Action(
			"xgettext " + "--omit-header --no-location " + XGETTEXT_COMMON_ARGS, "Generating pot file $TARGET"
		),
		suffix=".pot",
	)
