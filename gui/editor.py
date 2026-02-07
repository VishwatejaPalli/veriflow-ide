import importlib
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, cast

from PySide6.QtCore import QRegularExpression, Qt, Signal
from PySide6.QtGui import QColor, QFont, QTextCharFormat, QSyntaxHighlighter, QTextCursor, QPainter, QTextDocument
from PySide6.QtWidgets import QPlainTextEdit, QTabWidget, QVBoxLayout, QWidget, QTextEdit

QsciLexerType = object
QsciScintillaType = object

DEFAULT_LANGUAGE = "verilog"
DEFAULT_FONT_SIZE = 11
DEFAULT_FONT_FAMILY = "Fira Code"

# Case-insensitive regex option constant placed before schemes for availability
CASE_INSENSITIVE = QRegularExpression.PatternOption.CaseInsensitiveOption

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

# Color schemes for editor
COLOR_SCHEME = {
	"current_line": QColor("#E8F2FF"),
	"line_number_bg": QColor("#F0F0F0"),
	"line_number_fg": QColor("#666666"),
	"brace_match": QColor("#90EE90"),
	"brace_unmatch": QColor("#FF6B6B"),
}

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


class LineNumberArea(QWidget):
	"""Line number area widget for QPlainTextEdit."""

	def __init__(self, editor):
		super().__init__(editor)
		self.editor = editor

	def sizeHint(self):
		return self.editor.line_number_area_width()

	def paintEvent(self, event):
		self.editor.line_number_area_paint_event(event)


class KeywordHighlighter(QSyntaxHighlighter):
	"""Fallback syntax highlighting when QScintilla is missing.
	
	Provides regex-based syntax highlighting for Verilog, SystemVerilog, and C++.
	Supports keywords, strings, numbers, comments, and language-specific directives.
	"""

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
		# Optimize: combine keywords into single regex pattern
		pattern_str = r"\b(" + "|".join(re.escape(word) for word in unique) + r")\b"
		pattern = QRegularExpression(pattern_str)
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
	"""Main editor widget supporting both QScintilla and QPlainTextEdit.
	
	Features:
	- Syntax highlighting for Verilog, SystemVerilog, and C++
	- Line numbers
	- Current line highlighting
	- Brace matching (QScintilla only)
	- Code folding (QScintilla only)
	- Find/replace
	- Comment toggling
	- Indent/dedent
	- Zoom controls
	- Dirty state tracking
	"""
	dirtyChanged = Signal(bool)

	def __init__(self, parent=None):
		super().__init__(parent)
		self.file_path = None
		self._untitled_label = None
		self._dirty = False
		self._suspend_dirty = False
		self.language = DEFAULT_LANGUAGE
		self._current_font = QFont(DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE)
		self._lexer = None
		self.highlighter = None
		self.line_number_area = None
		layout = QVBoxLayout()
		
		if QsciScintilla is not None:
			self.editor = QsciScintilla()
			self._configure_qscintilla()
		else:
			self.editor = QPlainTextEdit()
			self.editor.setPlaceholderText("Syntax highlighting enabled")
			self.editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
			self._configure_plain_text_editor()
			
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
	
	def find_text(self, text, case_sensitive=False, whole_words=False, regex=False):
		"""Find text in the editor."""
		if not text:
			return False
		
		if QsciScintilla is not None and isinstance(self.editor, QsciScintilla):
			# Use QScintilla find
			try:
				return self.editor.findFirst(  # type: ignore
					text, regex, case_sensitive, whole_words,
					True,  # wrap
					True   # forward
				)
			except (TypeError, AttributeError):
				pass
		
		# Use QPlainTextEdit find
		if isinstance(self.editor, QPlainTextEdit):
			flags = QTextDocument.FindFlag(0)
			if case_sensitive:
				flags |= QTextDocument.FindFlag.FindCaseSensitively
			if whole_words:
				flags |= QTextDocument.FindFlag.FindWholeWords
			
			cursor = self.editor.textCursor()  # type: ignore
			new_cursor = self.editor.document().find(text, cursor, flags)  # type: ignore
			
			if not new_cursor.isNull():
				self.editor.setTextCursor(new_cursor)  # type: ignore
				return True
			# Wrap around
			new_cursor = self.editor.document().find(text, 0, flags)  # type: ignore
			if not new_cursor.isNull():
				self.editor.setTextCursor(new_cursor)  # type: ignore
				return True
		return False
	
	def find_next(self):
		"""Find next occurrence."""
		if QsciScintilla is not None and isinstance(self.editor, QsciScintilla):
			try:
				self.editor.findNext()  # type: ignore
			except AttributeError:
				pass
	
	def replace_text(self, find_text, replace_with, case_sensitive=False):
		"""Replace current selection if it matches find_text."""
		if not find_text:
			return False
		
		if isinstance(self.editor, QPlainTextEdit):
			cursor = self.editor.textCursor()
			if cursor.hasSelection():
				selected = cursor.selectedText()
				matches = (selected == find_text if case_sensitive else 
				          selected.lower() == find_text.lower())
				if matches:
					cursor.insertText(replace_with)
					return True
		return False
	
	def replace_all(self, find_text, replace_with, case_sensitive=False):
		"""Replace all occurrences."""
		if not find_text:
			return 0
		
		count = 0
		if isinstance(self.editor, QPlainTextEdit):
			cursor = QTextCursor(self.editor.document())
			cursor.beginEditBlock()
			
			flags = QTextDocument.FindFlag(0)
			if case_sensitive:
				flags |= QTextDocument.FindFlag.FindCaseSensitively
			
			while True:
				cursor = self.editor.document().find(find_text, cursor, flags)
				if cursor.isNull():
					break
				cursor.insertText(replace_with)
				count += 1
			
			cursor.endEditBlock()
		return count
	
	def toggle_comment(self):
		"""Toggle line comments for selected lines."""
		if not isinstance(self.editor, QPlainTextEdit):
			return
		
		cursor = self.editor.textCursor()
		start = cursor.selectionStart()
		end = cursor.selectionEnd()
		
		# Get the block range
		cursor.setPosition(start)
		start_block = cursor.blockNumber()
		cursor.setPosition(end)
		end_block = cursor.blockNumber()
		
		# Check if all lines are commented
		cursor.setPosition(start)
		all_commented = True
		for i in range(start_block, end_block + 1):
			cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
			block_text = cursor.block().text().lstrip()
			if not block_text.startswith("//"):
				all_commented = False
				break
			cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
		
		# Toggle comments
		cursor.setPosition(start)
		cursor.beginEditBlock()
		
		for i in range(start_block, end_block + 1):
			cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
			if all_commented:
				# Remove comment
				block_text = cursor.block().text()
				comment_pos = block_text.find("//")
				if comment_pos >= 0:
					cursor.movePosition(QTextCursor.MoveOperation.Right, 
					                   QTextCursor.MoveMode.MoveAnchor, comment_pos)
					cursor.deleteChar()
					cursor.deleteChar()
					if cursor.block().text()[comment_pos:comment_pos+1] == " ":
						cursor.deleteChar()
			else:
				# Add comment
				cursor.insertText("// ")
			
			cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
		
		cursor.endEditBlock()
	
	def zoom_in(self):
		"""Increase font size."""
		if QsciScintilla is not None and isinstance(self.editor, QsciScintilla):
			try:
				self.editor.zoomIn()  # type: ignore
			except AttributeError:
				pass
		else:
			try:
				font = self.editor.font()  # type: ignore
				size = font.pointSize()
				if size < 72:
					font.setPointSize(size + 1)
					self.set_editor_font(font)
			except AttributeError:
				pass
	
	def zoom_out(self):
		"""Decrease font size."""
		if QsciScintilla is not None and isinstance(self.editor, QsciScintilla):
			try:
				self.editor.zoomOut()  # type: ignore
			except AttributeError:
				pass
		else:
			try:
				font = self.editor.font()  # type: ignore
				size = font.pointSize()
				if size > 6:
					font.setPointSize(size - 1)
					self.set_editor_font(font)
			except AttributeError:
				pass
	
	def reset_zoom(self):
		"""Reset font size to default."""
		if QsciScintilla is not None and isinstance(self.editor, QsciScintilla):
			try:
				self.editor.zoomTo(0)  # type: ignore
			except AttributeError:
				pass
		else:
			font = QFont(DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE)
			self.set_editor_font(font)
	
	def indent(self):
		"""Indent selected lines or current line."""
		if not isinstance(self.editor, QPlainTextEdit):
			return
		
		cursor = self.editor.textCursor()
		start = cursor.selectionStart()
		end = cursor.selectionEnd()
		
		cursor.setPosition(start)
		start_block = cursor.blockNumber()
		cursor.setPosition(end)
		end_block = cursor.blockNumber()
		
		cursor.setPosition(start)
		cursor.beginEditBlock()
		
		for i in range(start_block, end_block + 1):
			cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
			cursor.insertText("    ")  # 4 spaces
			cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
		
		cursor.endEditBlock()
	
	def dedent(self):
		"""Dedent selected lines or current line."""
		if not isinstance(self.editor, QPlainTextEdit):
			return
		
		cursor = self.editor.textCursor()
		start = cursor.selectionStart()
		end = cursor.selectionEnd()
		
		cursor.setPosition(start)
		start_block = cursor.blockNumber()
		cursor.setPosition(end)
		end_block = cursor.blockNumber()
		
		cursor.setPosition(start)
		cursor.beginEditBlock()
		
		for i in range(start_block, end_block + 1):
			cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
			block_text = cursor.block().text()
			
			# Remove up to 4 leading spaces or 1 tab
			if block_text.startswith("    "):
				for _ in range(4):
					cursor.deleteChar()
			elif block_text.startswith("\t"):
				cursor.deleteChar()
			elif block_text.startswith(" "):
				# Remove any leading spaces (up to 4)
				spaces = len(block_text) - len(block_text.lstrip(' '))
				for _ in range(min(spaces, 4)):
					cursor.deleteChar()
			
			cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
		
		cursor.endEditBlock()
	
	def get_cursor_position(self):
		"""Get current cursor position (line, column)."""
		try:
			if QsciScintilla is not None and isinstance(self.editor, QsciScintilla):
				line, col = self.editor.getCursorPosition()  # type: ignore
				return (line + 1, col + 1)  # Convert to 1-based
		except (TypeError, AttributeError):
			pass
		
		try:
			cursor = self.editor.textCursor()  # type: ignore
			line = cursor.blockNumber() + 1
			col = cursor.columnNumber() + 1
			return (line, col)
		except AttributeError:
			return (1, 1)
	
	def get_selection(self):
		"""Get currently selected text."""
		if QsciScintilla is not None and isinstance(self.editor, QsciScintilla):
			try:
				return self.editor.selectedText()  # type: ignore
			except AttributeError:
				pass
		
		try:
			return self.editor.textCursor().selectedText()  # type: ignore
		except AttributeError:
			return ""
	
	def has_selection(self):
		"""Check if there is selected text."""
		if QsciScintilla is not None and isinstance(self.editor, QsciScintilla):
			try:
				return self.editor.hasSelectedText()  # type: ignore
			except AttributeError:
				pass
		
		try:
			return self.editor.textCursor().hasSelection()  # type: ignore
		except AttributeError:
			return False

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
		
		if QsciScintilla is not None and isinstance(self.editor, QsciScintilla):
			# Use QScintilla lexer if available
			if lexer_cls:
				try:
					self._lexer = lexer_cls(self.editor)  # type: ignore
					self._lexer.setDefaultFont(self._current_font)  # type: ignore
					self.editor.setLexer(self._lexer)  # type: ignore
				except (TypeError, AttributeError):
					pass
		elif self.highlighter is not None:
			# Use fallback highlighter for QPlainTextEdit
			self.highlighter.set_language(self.language)
	
	def _configure_qscintilla(self):
		"""Configure QScintilla editor with advanced features.
		
		Note: QsciScintilla is not available in PySide6. This is a placeholder
		for future compatibility if QsciScintilla support is added.
		"""
		if QsciScintilla is None:
			return
		
		if not isinstance(self.editor, QsciScintilla):
			return
		
		# Type: ignore because these methods are only available on QsciScintilla
		try:
			editor: QsciScintillaType = self.editor  # type: ignore
			
			# Line numbers
			editor.setMarginType(0, QsciScintilla.NumberMargin)  # type: ignore
			editor.setMarginWidth(0, "00000")  # type: ignore
			editor.setMarginsForegroundColor(COLOR_SCHEME["line_number_fg"])  # type: ignore
			editor.setMarginsBackgroundColor(COLOR_SCHEME["line_number_bg"])  # type: ignore
			
			# Current line highlighting
			editor.setCaretLineVisible(True)  # type: ignore
			editor.setCaretLineBackgroundColor(COLOR_SCHEME["current_line"])  # type: ignore
			
			# Brace matching
			editor.setBraceMatching(QsciScintilla.SloppyBraceMatch)  # type: ignore
			editor.setMatchedBraceBackgroundColor(COLOR_SCHEME["brace_match"])  # type: ignore
			editor.setUnmatchedBraceBackgroundColor(COLOR_SCHEME["brace_unmatch"])  # type: ignore
			
			# Indentation guides
			editor.setIndentationGuides(True)  # type: ignore
			
			# Auto-indentation
			editor.setAutoIndent(True)  # type: ignore
			editor.setTabWidth(4)  # type: ignore
			editor.setIndentationsUseTabs(False)  # type: ignore
			
			# Folding
			editor.setFolding(QsciScintilla.BoxedTreeFoldStyle)  # type: ignore
			editor.setMarginWidth(2, 12)  # type: ignore
			
			# Disable wrapping
			editor.setWrapMode(QsciScintilla.WrapNone)  # type: ignore
			
			# UTF-8 encoding
			editor.setUtf8(True)  # type: ignore
		except (AttributeError, TypeError):
			# QsciScintilla methods not available, skip configuration
			pass
	
	def _configure_plain_text_editor(self):
		"""Configure QPlainTextEdit with line numbers and highlighting."""
		if not isinstance(self.editor, QPlainTextEdit):
			return
		
		editor = self.editor
		
		# Enable syntax highlighting
		self.highlighter = KeywordHighlighter(editor.document())
		
		# Line numbers
		self.line_number_area = LineNumberArea(self)
		editor.blockCountChanged.connect(self.update_line_number_area_width)
		editor.updateRequest.connect(self.update_line_number_area)
		editor.cursorPositionChanged.connect(self.highlight_current_line)
		
		self.update_line_number_area_width(0)
		self.highlight_current_line()
		
		# Tab settings - 4 spaces
		font_metrics = editor.fontMetrics()
		editor.setTabStopDistance(4 * font_metrics.horizontalAdvance(' '))
	
	def line_number_area_width(self):
		"""Calculate the width needed for line numbers."""
		if not isinstance(self.editor, QPlainTextEdit):
			return 0
		
		digits = 1
		max_num = max(1, self.editor.blockCount())
		while max_num >= 10:
			max_num //= 10
			digits += 1
		
		space = 10 + self.editor.fontMetrics().horizontalAdvance('9') * digits
		return space
	
	def update_line_number_area_width(self, _):
		"""Update the width of the line number area."""
		if isinstance(self.editor, QPlainTextEdit) and self.line_number_area:
			self.editor.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
	
	def update_line_number_area(self, rect, dy):
		"""Update the line number area when scrolling."""
		if not isinstance(self.editor, QPlainTextEdit) or not self.line_number_area:
			return
		
		if dy:
			self.line_number_area.scroll(0, dy)
		else:
			self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
		
		if rect.contains(self.editor.viewport().rect()):
			self.update_line_number_area_width(0)
	
	def line_number_area_paint_event(self, event):
		"""Paint the line numbers."""
		if not isinstance(self.editor, QPlainTextEdit) or not self.line_number_area:
			return
		
		painter = QPainter(self.line_number_area)
		painter.fillRect(event.rect(), COLOR_SCHEME["line_number_bg"])
		
		block = self.editor.firstVisibleBlock()
		block_number = block.blockNumber()
		top = self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top()
		bottom = top + self.editor.blockBoundingRect(block).height()
		
		while block.isValid() and top <= event.rect().bottom():
			if block.isVisible() and bottom >= event.rect().top():
				number = str(block_number + 1)
				painter.setPen(COLOR_SCHEME["line_number_fg"])
				painter.drawText(0, int(top), self.line_number_area.width() - 5,
				               self.editor.fontMetrics().height(),
				               Qt.AlignmentFlag.AlignRight, number)
			
			block = block.next()
			top = bottom
			bottom = top + self.editor.blockBoundingRect(block).height()
			block_number += 1
	
	def highlight_current_line(self):
		"""Highlight the current line in QPlainTextEdit."""
		if not isinstance(self.editor, QPlainTextEdit):
			return
		
		extra_selections = []
		
		if not self.editor.isReadOnly():
			selection = QTextEdit.ExtraSelection()
			selection.format.setBackground(COLOR_SCHEME["current_line"])
			selection.format.setProperty(QTextCharFormat.Property.FullWidthSelection, True)
			selection.cursor = self.editor.textCursor()
			selection.cursor.clearSelection()
			extra_selections.append(selection)
		
		self.editor.setExtraSelections(extra_selections)
	
	def resizeEvent(self, event):
		"""Handle resize events for line number area."""
		super().resizeEvent(event)
		if isinstance(self.editor, QPlainTextEdit) and self.line_number_area:
			cr = self.editor.contentsRect()
			self.line_number_area.setGeometry(cr.left(), cr.top(),
			                                 self.line_number_area_width(), cr.height())

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
	"""Tab widget for managing multiple editor instances.
	
	Features:
	- Multi-document interface
	- Drag-and-drop tab reordering
	- Dirty state indicators
	- Automatic untitled document naming
	- Tab closing with cleanup
	"""
	currentFileChanged = Signal(object)  # emits active path or None

	def __init__(self, parent=None):
		super().__init__(parent)
		self.setTabsClosable(True)
		self.setDocumentMode(True)
		self.setMovable(True)  # Enable tab drag-and-drop reordering
		self._default_font = QFont(DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE)
		self._untitled_counter = 0
		self.tabCloseRequested.connect(self._close_tab)
		self.currentChanged.connect(lambda _: self.currentFileChanged.emit(self.current_file_path()))
		self.currentFileChanged.emit(None)

	def new_document(self):
		"""Create a new untitled document.
		
		Returns:
			EditorWidget instance
		"""
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
		"""Open a file in a new tab or focus existing tab.
		
		Args:
			path: File path to open
			text: Content of the file
			
		Returns:
			EditorWidget instance or None
		"""
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
	
	def close_all_tabs(self):
		"""Close all tabs."""
		while self.count() > 0:
			self._close_tab(0)
	
	def close_other_tabs(self, index):
		"""Close all tabs except the specified one."""
		if index < 0 or index >= self.count():
			return
		
		# Close tabs after the specified index
		for i in range(self.count() - 1, index, -1):
			self._close_tab(i)
		
		# Close tabs before the specified index
		for i in range(index - 1, -1, -1):
			self._close_tab(i)

	def set_global_font(self, font):
		if not font:
			return
		self._default_font = font
		for index in range(self.count()):
			editor = self.widget(index)
			if isinstance(editor, EditorWidget):
				editor.set_editor_font(font)
