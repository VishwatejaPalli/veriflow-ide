import importlib
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, cast

from PySide6.QtCore import QRegularExpression, Qt, Signal
from PySide6.QtGui import QColor, QFont, QTextCharFormat, QSyntaxHighlighter, QTextCursor
from PySide6.QtWidgets import QPlainTextEdit, QTabWidget, QVBoxLayout, QWidget

QsciLexerType = object
QsciScintillaType = object

DEFAULT_LANGUAGE = "verilog"

# Case-insensitive regex option constant placed before schemes for availability
CASE_INSENSITIVE = QRegularExpression.PatternOption.CaseInsensitiveOption

# Fast mode: prefer responsiveness over visual features like highlighting

KEYWORD_SETS = {
	"verilog": [
		"module",
		"endmodule",
		"input",
		"output",
		"inout",
		"wire",
		"reg",
		"logic",
		"always",
		"always_ff",
		"always_comb",
		"posedge",
		"negedge",
		"assign",
		"begin",
		"end",
		"case",
		"endcase",
		"generate",
		"endgenerate",
		"parameter",
		"localparam",
		"typedef",
		"function",
		"task",
		"initial",
	],
	"systemverilog": [
		"logic",
		"bit",
		"byte",
		"struct",
		"enum",
		"interface",
		"clocking",
		"package",
		"import",
		"export",
		"unique",
		"priority",
		"inside",
		"rand",
		"randc",
		"covergroup",
		"coverpoint",
		"constraint",
		"with",
	],
	"cpp": [
		"class",
		"struct",
		"template",
		"typename",
		"if",
		"else",
		"for",
		"while",
		"switch",
		"case",
		"break",
		"continue",
		"return",
		"namespace",
		"using",
		"public",
		"private",
		"protected",
		"virtual",
		"override",
		"constexpr",
		"inline",
	],
}
KEYWORD_SETS["systemverilog"] = KEYWORD_SETS["verilog"] + KEYWORD_SETS["systemverilog"]

EXTENSION_LANGUAGE = {
	".v": "verilog",
	".vh": "verilog",
	".sv": "systemverilog",
	".svh": "systemverilog",
	".c": "cpp",
	".cc": "cpp",
	".cpp": "cpp",
	".cxx": "cpp",
	".h": "cpp",
	".hh": "cpp",
	".hpp": "cpp",
	".hxx": "cpp",
}

FALLBACK_SCHEMES = {
		"verilog": {
			"keywords": KEYWORD_SETS["verilog"],
			"regex_rules": [
				{"pattern": r"`[a-zA-Z_]\\w*", "format": "directive"},
				{"pattern": r"\\$[a-zA-Z_]\\w*", "format": "system"},
				{
					"pattern": r"\\b\\d+'[bodh][0-9a-fxz_]+\\b|\\b\\d+\\b",
					"format": "number",
					"options": CASE_INSENSITIVE,
				},
				{"pattern": r'"([^"\\\\]|\\\\.)*"', "format": "string"},
			],
			"line_comment": r"//[^\n]*",
			"block_comment": ("/*", "*/"),
		},
		"systemverilog": {
			"keywords": KEYWORD_SETS["systemverilog"],
			"regex_rules": [
				{"pattern": r"`[a-zA-Z_]\\w*", "format": "directive"},
				{"pattern": r"\\$[a-zA-Z_]\\w*", "format": "system"},
				{
					"pattern": r"\\b\\d+'[bodh][0-9a-fxz_]+\\b|\\b\\d+\\b",
					"format": "number",
					"options": CASE_INSENSITIVE,
				},
				{"pattern": r'"([^"\\\\]|\\\\.)*"', "format": "string"},
				{"pattern": r"'([^'\\\\]|\\\\.)*'", "format": "char"},
			],
			"line_comment": r"//[^\n]*",
			"block_comment": ("/*", "*/"),
		},
		"cpp": {
			"keywords": KEYWORD_SETS["cpp"],
			"regex_rules": [
				{"pattern": r"#\\s*[a-zA-Z_]\\w*", "format": "directive"},
				{
					"pattern": r"\\b0x[0-9a-fA-F]+\\b|\\b\\d+(?:\\.\\d+)?(?:[eE][+-]?\\d+)?\\b",
					"format": "number",
				},
				{"pattern": r'"([^"\\\\]|\\\\.)*"', "format": "string"},
				{"pattern": r"'([^'\\\\]|\\\\.)*'", "format": "char"},
			],
			"line_comment": r"//[^\n]*",
			"block_comment": ("/*", "*/"),
		},
	}
FALLBACK_SCHEMES["default"] = FALLBACK_SCHEMES["verilog"]


QsciScintilla: Optional[type[QsciScintillaType]] = None
LEXER_CLASS_MAP: Dict[str, type[QsciLexerType]] = {}
try:  # pragma: no cover - optional dependency
	qsci_module = importlib.import_module("PySide6.Qsci")
	QsciScintilla = getattr(qsci_module, "QsciScintilla")

	def _register_lexer(language, attr_name):
		cls = getattr(qsci_module, attr_name, None)
		if cls is not None:
			LEXER_CLASS_MAP[language] = cls

	_register_lexer("verilog", "QsciLexerVerilog")
	_register_lexer("systemverilog", "QsciLexerSystemVerilog")
	_register_lexer("cpp", "QsciLexerCPP")
	HAVE_QSCINTILLA = True
except ModuleNotFoundError:  # pragma: no cover - optional dependency
	HAVE_QSCINTILLA = False


class KeywordHighlighter(QSyntaxHighlighter):
	"""Fallback syntax highlighting when QScintilla is missing."""

	def __init__(self, document):
		super().__init__(document)
		self._language = DEFAULT_LANGUAGE
		self._rules = []
		self._line_comment_pattern = QRegularExpression(r"//[^\n]*")
		self._block_comment_tokens = ("/*", "*/")
		self._formats = {
			"keyword": self._build_format("#0c5ed7", bold=True),
			"string": self._build_format("#008000"),
			"char": self._build_format("#008000"),
			"number": self._build_format("#c18401"),
			"directive": self._build_format("#af00db", bold=True),
			"system": self._build_format("#d57245"),
			"comment": self._build_format("#6a737d", italic=True),
		}

	def _build_format(self, color_hex, bold=False, italic=False):
		fmt = QTextCharFormat()
		fmt.setForeground(QColor(color_hex))
		if bold:
			fmt.setFontWeight(int(QFont.Weight.Bold))
		if italic:
			fmt.setFontItalic(True)
		return fmt

	def set_language(self, language):
		self._language = language or DEFAULT_LANGUAGE
		scheme = FALLBACK_SCHEMES.get(self._language, FALLBACK_SCHEMES["default"])
		self._rules = []
		self._install_keyword_rules(scheme.get("keywords", []))
		for rule in scheme.get("regex_rules", []):
			fmt = self._formats.get(rule["format"], self._formats["keyword"])
			regex = QRegularExpression(rule["pattern"])
			if "options" in rule:
				regex.setPatternOptions(rule["options"])
			self._rules.append((regex, fmt))
		self._line_comment_pattern = None
		line_comment = scheme.get("line_comment")
		if line_comment:
			self._line_comment_pattern = QRegularExpression(line_comment)
		self._block_comment_tokens = scheme.get("block_comment", ("/*", "*/"))
		self.rehighlight()

	def _install_keyword_rules(self, keywords):
		if not keywords:
			return
		unique = sorted(set(keywords))
		if not unique:
			return
		for word in unique:
			pattern = QRegularExpression(rf"\\b{re.escape(word)}\\b")
			pattern.setPatternOptions(CASE_INSENSITIVE)
			self._rules.append((pattern, self._formats["keyword"]))

	def highlightBlock(self, text):  # noqa: N802 - Qt API signature
		for pattern, fmt in self._rules:
			iterator = pattern.globalMatch(text)
			while iterator.hasNext():
				match = iterator.next()
				self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

		if self._line_comment_pattern:
			iterator = self._line_comment_pattern.globalMatch(text)
			while iterator.hasNext():
				match = iterator.next()
				self.setFormat(match.capturedStart(), match.capturedLength(), self._formats["comment"])

		self._apply_block_comments(text)

	def _apply_block_comments(self, text):
		start_token, end_token = self._block_comment_tokens
		if not start_token or not end_token:
			return
		self.setCurrentBlockState(0)
		start_index = 0
		if self.previousBlockState() != 1:
			start_index = text.find(start_token)
		else:
			start_index = 0
		while start_index >= 0:
			end_index = text.find(end_token, start_index + len(start_token))
			if end_index == -1:
				length = len(text) - start_index
				self.setCurrentBlockState(1)
			else:
				length = end_index - start_index + len(end_token)
			self.setFormat(start_index, length, self._formats["comment"])
			if end_index == -1:
				break
			start_index = text.find(start_token, start_index + length)


class EditorWidget(QWidget):
	dirtyChanged = Signal(bool)

	def __init__(self, parent=None):
		super().__init__(parent)
		self.file_path = None
		self._untitled_label = None
		self._dirty = False
		self._suspend_dirty = False
		self.language = DEFAULT_LANGUAGE
		self._current_font = QFont("Fira Code", 11)
		self._lexer = None
		self.highlighter = None
		layout = QVBoxLayout()
		if QsciScintilla is not None:
			self.editor = QsciScintilla()
			# Fast: disable wrapping and avoid extra decorations/features
			set_wrap = getattr(self.editor, "setWrapMode", None)
			wrap_none = getattr(QsciScintilla, "WrapNone", None)
			if callable(set_wrap):
				set_wrap(wrap_none if wrap_none is not None else 0)
		else:
			self.editor = QPlainTextEdit()
			self.editor.setPlaceholderText("Basic highlight mode (QScintilla missing)")
			# Fast: avoid costly wrapping
			self.editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
			self.highlighter = None
		layout.addWidget(cast(QWidget, self.editor))
		self.setLayout(layout)
		sig = getattr(self.editor, "textChanged", None)
		connect = getattr(sig, "connect", None)
		if callable(connect):
			connect(self._handle_text_changed)
		self.set_language(DEFAULT_LANGUAGE)
		self.set_editor_font(self._current_font)

	def set_text(self, text):
		self._suspend_dirty = True
		w = self.editor
		setter = getattr(w, "setText", None)
		if callable(setter):
			setter(text)
		else:
			plain = getattr(self.editor, "setPlainText", None)
			if callable(plain):
				plain(text)
		self._suspend_dirty = False

	def get_text(self):
		w = self.editor
		getter = getattr(w, "text", None)
		if callable(getter):
			return getter()
		to_plain = getattr(self.editor, "toPlainText", None)
		return to_plain() if callable(to_plain) else ""

	def clear(self):
		self.set_text("")
		self.mark_dirty()

	def widget(self):
		return self.editor

	def set_editor_font(self, font):
		if not font:
			return
		self._current_font = font
		set_font = getattr(self.editor, "setFont", None)
		if callable(set_font):
			set_font(font)
		w = self.editor
		margins_font = getattr(w, "setMarginsFont", None)
		if callable(margins_font):
			margins_font(font)
			lexer_fn = getattr(w, "lexer", None)
			if callable(lexer_fn):
				lex = lexer_fn()
				if lex is not None:
					set_def = getattr(lex, "setDefaultFont", None)
					if callable(set_def):
						set_def(font)
		else:
			doc = getattr(self.editor, "document", None)
			set_def = getattr(doc, "setDefaultFont", None)
			if callable(set_def):
				set_def(font)

	def editor_font(self):
		return self._current_font

	def set_file_path(self, path):
		self.file_path = path
		if path:
			self._untitled_label = None
		self.set_language(self._language_from_path(path))

	def display_name(self):
		base = Path(self.file_path).name if self.file_path else (self._untitled_label or "Untitled")
		return f"{base}*" if self._dirty else base

	def set_untitled_label(self, label):
		self._untitled_label = label

	def mark_clean(self):
		self._set_dirty(False)

	def mark_dirty(self):
		self._set_dirty(True)

	def is_dirty(self):
		return self._dirty

	def focus_editor(self):
		focus = getattr(self.editor, "setFocus", None)
		if callable(focus):
			focus()

	def undo(self):
		w = self.editor
		fn = getattr(w, "undo", None)
		if callable(fn):
			fn()

	def redo(self):
		w = self.editor
		fn = getattr(w, "redo", None)
		if callable(fn):
			fn()

	def cut(self):
		w = self.editor
		fn = getattr(w, "cut", None)
		if callable(fn):
			fn()

	def copy(self):
		w = self.editor
		fn = getattr(w, "copy", None)
		if callable(fn):
			fn()

	def paste(self):
		w = self.editor
		fn = getattr(w, "paste", None)
		if callable(fn):
			fn()

	def select_all(self):
		w = self.editor
		fn = getattr(w, "selectAll", None)
		if callable(fn):
			fn()

	def goto_line(self, line):
		if line is None or line < 1:
			return
		target_row = max(0, line - 1)
		w = self.editor
		set_pos = getattr(w, "setCursorPosition", None)
		ensure_vis = getattr(w, "ensureLineVisible", None)
		if callable(set_pos) and callable(ensure_vis):
			set_pos(target_row, 0)
			ensure_vis(target_row)
		else:
			document = getattr(self.editor, "document", None)
			if document is None:
				return
			cursor = QTextCursor(document)
			cursor.movePosition(QTextCursor.MoveOperation.Start)
			for _ in range(target_row):
				cursor.movePosition(QTextCursor.MoveOperation.Down)
			stc = getattr(self.editor, "setTextCursor", None)
			if callable(stc):
				stc(cursor)
			center = getattr(self.editor, "centerCursor", None)
			if callable(center):
				center()

	def set_language(self, language):
		self.language = language or DEFAULT_LANGUAGE
		w = self.editor
		lexer_cls = LEXER_CLASS_MAP.get(self.language) or LEXER_CLASS_MAP.get(DEFAULT_LANGUAGE)
		# Fast: skip setting lexer/highlighter to maximize responsiveness
		if self.highlighter is not None:
			self.highlighter.set_language(self.language)

	def _language_from_path(self, path):
		if not path:
			return DEFAULT_LANGUAGE
		ext = Path(path).suffix.lower()
		return EXTENSION_LANGUAGE.get(ext, DEFAULT_LANGUAGE)

	def _handle_text_changed(self):
		if self._suspend_dirty:
			return
		self._set_dirty(True)

	def _set_dirty(self, dirty):
		dirty = bool(dirty)
		if dirty == self._dirty:
			return
		self._dirty = dirty
		self.dirtyChanged.emit(self._dirty)


class EditorTabs(QTabWidget):
	currentFileChanged = Signal(object)  # emits active path or None

	def __init__(self, parent=None):
		super().__init__(parent)
		self.setTabsClosable(True)
		self.setDocumentMode(True)
		self._default_font = QFont("Fira Code", 11)
		self._untitled_counter = 0
		self.tabCloseRequested.connect(self._close_tab)
		self.currentChanged.connect(lambda _: self.currentFileChanged.emit(self.current_file_path()))
		self.currentFileChanged.emit(None)

	def new_document(self):
		editor = EditorWidget()
		self._setup_editor(editor)
		self._assign_untitled_label(editor)
		editor.mark_dirty()
		index = self.addTab(editor, editor.display_name())
		self.setCurrentIndex(index)
		editor.focus_editor()
		self.currentFileChanged.emit(None)
		return editor

	def open_document(self, path, text):
		existing = self._find_tab_by_path(path)
		if existing is not None:
			editor_w = self.widget(existing)
			if isinstance(editor_w, EditorWidget):
				editor_w.set_text(text)
				editor_w.mark_clean()
			self.setCurrentIndex(existing)
			self._update_tab_title(existing)
			self.currentFileChanged.emit(path)
			return cast(EditorWidget, editor_w) if isinstance(editor_w, EditorWidget) else None
		editor = EditorWidget()
		self._setup_editor(editor)
		editor.set_text(text)
		editor.set_file_path(path)
		editor.mark_clean()
		index = self.addTab(editor, editor.display_name())
		self.setCurrentIndex(index)
		editor.focus_editor()
		self.currentFileChanged.emit(path)
		return editor

	def current_editor(self):
		w = self.widget(self.currentIndex())
		return cast(EditorWidget, w) if isinstance(w, EditorWidget) else None

	def current_file_path(self):
		editor = self.current_editor()
		return editor.file_path if isinstance(editor, EditorWidget) else None

	def set_current_file_path(self, path):
		editor = self.current_editor()
		if isinstance(editor, EditorWidget):
			editor.set_file_path(path)
			self._update_tab_title(self.currentIndex())
			self.currentFileChanged.emit(path)

	def set_editor_path(self, editor, path):
		if not editor:
			return
		if isinstance(editor, EditorWidget):
			editor.set_file_path(path)
		index = self.indexOf(editor)
		if index != -1:
			self._update_tab_title(index)
			if index == self.currentIndex():
				self.currentFileChanged.emit(path)

	def refresh_current_title(self):
		self._update_tab_title(self.currentIndex())

	def _find_tab_by_path(self, path):
		for index in range(self.count()):
			editor = self.widget(index)
			if isinstance(editor, EditorWidget) and editor.file_path and Path(editor.file_path) == Path(path):
				return index
		return None

	def _close_tab(self, index):
		widget = self.widget(index)
		if not widget:
			return
		self.removeTab(index)
		widget.deleteLater()
		self.currentFileChanged.emit(self.current_file_path())

	def _update_tab_title(self, index):
		if index < 0:
			return
		editor = self.widget(index)
		if isinstance(editor, EditorWidget):
			self.setTabText(index, editor.display_name())

	def _setup_editor(self, editor):
		if not editor:
			return
		editor.set_editor_font(self._default_font)
		editor.dirtyChanged.connect(lambda _dirty, ed=editor: self._handle_editor_dirty_changed(ed))

	def _handle_editor_dirty_changed(self, editor):
		index = self.indexOf(editor)
		if index != -1:
			self._update_tab_title(index)

	def _assign_untitled_label(self, editor):
		if not editor:
			return
		label = "Untitled" if self._untitled_counter == 0 else f"Untitled{self._untitled_counter}"
		self._untitled_counter += 1
		editor.set_untitled_label(label)

	def set_global_font(self, font):
		if not font:
			return
		self._default_font = font
		for index in range(self.count()):
			editor = self.widget(index)
			if isinstance(editor, EditorWidget):
				editor.set_editor_font(font)
