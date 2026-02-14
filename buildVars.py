# Build customizations
# Change this file instead of sconstruct or manifest files, whenever possible.

from site_scons.site_tools.NVDATool.typings import AddonInfo, BrailleTables, SymbolDictionaries

# Since some strings in `addon_info` are translatable,
# we need to include them in the .po files.
# Gettext recognizes only strings given as parameters to the `_` function.
# To avoid initializing translations in this module we simply import a "fake" `_` function
# which returns whatever is given to it as an argument.
from site_scons.site_tools.NVDATool.utils import _


addon_info = AddonInfo(
	addon_name="hangulBlockSplitter",
	# Translators: Summary/title for this add-on shown in Add-ons Manager/store listings.
	addon_summary=_("Hangul Block Splitter"),
	# Translators: Long description for this add-on shown in add-on information pages.
	addon_description=_(
		"Splits selected Hangul text or the Hangul block under cursor into Jamo, "
		"then reads, describes, or copies the result."
	),
	addon_version="1.0",
	# Translators: Brief changelog entry for this add-on version.
	addon_changelog=_(
		"Initial NVDA add-on release with selection-aware splitting, Hangul-only "
		"filtering, and an interactive splitter dialog."
	),
	addon_author="VIPPotato <vippotato1@tyflodysk.pl>",
	addon_url="https://github.com/VIPPotato/hangul-block-splitter-nvda",
	addon_sourceURL="https://github.com/VIPPotato/hangul-block-splitter-nvda",
	addon_docFileName="readme.html",
	addon_minimumNVDAVersion="2025.3",
	addon_lastTestedNVDAVersion="2026.1",
	addon_updateChannel=None,
	addon_license="GPL v2",
	addon_licenseURL="https://www.gnu.org/licenses/old-licenses/gpl-2.0.html",
)

# Python sources included in translation extraction and dependency tracking.
pythonSources: list[str] = ["addon/globalPlugins/*.py"]

# Files that contain strings for translation.
i18nSources: list[str] = pythonSources + ["buildVars.py"]

# Files ignored when creating the .nvda-addon bundle.
excludedFiles: list[str] = ["globalPlugins/__pycache__/*"]

# Base language for generated documentation.
baseLanguage: str = "en"

# Additional Markdown extensions for docs conversion.
markdownExtensions: list[str] = []

# This add-on does not define custom braille tables.
brailleTables: BrailleTables = {}

# This add-on does not define custom speech symbol dictionaries.
symbolDictionaries: SymbolDictionaries = {}
