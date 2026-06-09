# __init__.py
# Copyright (C) 2026 Chai Chaimee
# Licensed under GNU General Public License. See COPYING.txt for details.

import os
import re
import json
import shutil
import winsound
import weakref
import threading
import addonHandler
import globalPluginHandler
import api
import ui
import textInfos
import speech
import scriptHandler
import core
import config
from logHandler import log

addonHandler.initTranslation()

USER_CONFIG_PATH = config.getUserDefaultConfigPath()
NEW_CONFIG_SUBDIR = "ChaiChaimee"
NEW_CONFIG_PATH = os.path.join(USER_CONFIG_PATH, NEW_CONFIG_SUBDIR)

HISTORY_FILE = "cmdreader_history.json"
NEW_HISTORY_FILE = os.path.join(NEW_CONFIG_PATH, HISTORY_FILE)

CMDREADER_LOG_FILENAME = "CMDReader.txt"
NEW_HISTORY_LOG = os.path.join(NEW_CONFIG_PATH, CMDREADER_LOG_FILENAME)

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = _("CMDReader")

	# Updated regex to use pure standard Python character classes, avoiding unsupported \P escapes
	_prompt_regex = re.compile(r'^[A-Za-z]:\\.*>\s*$|^>\s*$|^[A-Za-z0-9_\-]+@[A-Za-z0-9_\-]+:.*[\$\s]*$')
	
	_error_keywords = [
		"is not recognized as an internal or external command",
		"access denied",
		"error 404",
		"fatal error",
		"failed to",
		"exception occurred"
	]

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._shadow_records = []
		self._current_line_index = -1
		self._last_raw_text = ""
		self._is_monitoring = False
		self._last_processed_line_count = 0
		self._command_running = False
		self._lock = threading.Lock()
		self._current_obj_ref = None

		self.log_path = NEW_HISTORY_LOG

		core.callLater(500, self._clear_log)
		self._ensure_config_dir()
		self._migrate_old_paths()
		self._load_history()

	def _ensure_config_dir(self):
		try:
			os.makedirs(NEW_CONFIG_PATH, exist_ok=True)
		except Exception as e:
			log.error(f"CMDReader: Directory creation failed: {e}")

	def _migrate_old_paths(self):
		old_history = os.path.join(USER_CONFIG_PATH, HISTORY_FILE)
		old_log = os.path.join(USER_CONFIG_PATH, CMDREADER_LOG_FILENAME)

		if os.path.isfile(old_history):
			try:
				self._ensure_config_dir()
				shutil.move(old_history, NEW_HISTORY_FILE)
			except Exception as e:
				log.error(f"CMDReader: History migration failed: {e}")

		if os.path.isfile(old_log):
			try:
				self._ensure_config_dir()
				shutil.move(old_log, NEW_HISTORY_LOG)
			except Exception as e:
				log.error(f"CMDReader: Log migration failed: {e}")

	def _load_history(self):
		if not os.path.isfile(NEW_HISTORY_FILE):
			return
		try:
			with open(NEW_HISTORY_FILE, "r", encoding="utf-8") as f:
				data = json.load(f)
			if isinstance(data, list):
				self._shadow_records = data
		except Exception as e:
			log.error(f"CMDReader: Failed to load history: {e}")

	def _save_history(self):
		try:
			self._ensure_config_dir()
			with open(NEW_HISTORY_FILE, "w", encoding="utf-8") as f:
				json.dump(self._shadow_records, f, ensure_ascii=False, indent=2)
		except Exception as e:
			log.error(f"CMDReader: Failed to save history: {e}")

	def _is_cmd_window(self, obj):
		if not obj:
			return False
		try:
			app_module = obj.appModule
			if not app_module:
				return False
			app_name = app_module.appName.lower()
			if app_name in ["cmd", "powershell", "pwsh", "windowsterminal"]:
				return True
			
			window_class = getattr(obj, "windowClassName", "").lower()
			if "consolewindowclass" in window_class or "cascadiapanelclass" in window_class:
				return True
		except (AttributeError, RuntimeError):
			pass
		return False

	def _clear_log(self):
		try:
			with open(self.log_path, "w", encoding="utf-8") as f:
				f.write("")
		except Exception as e:
			log.error(f"CMDReader: Clear log failed: {e}")

	def _clean_line_formatting(self, text):
		if not text:
			return ""
		lines = [cleaned for line in text.splitlines() if (cleaned := line.rstrip())]
		return "\n".join(lines)

	def _trim_to_first_prompt(self, text):
		if not text:
			return ""
		lines = text.splitlines()
		for i, line in enumerate(lines):
			if self._prompt_regex.search(line):
				return "\n".join(lines[i:])
		return text

	def _filter_noise(self, line):
		clean = line.strip()
		if not clean or re.match(r'^[=\-_*#]{3,}$', clean):
			return False
		return True

	def _write_log(self, text):
		trimmed = self._trim_to_first_prompt(text)
		clean_data = self._clean_line_formatting(trimmed)
		lines = clean_data.splitlines()
		filtered = [line for line in lines if not self._prompt_regex.match(line) and self._filter_noise(line)]
		final_text = "\n".join(filtered)
		try:
			with open(self.log_path, "w", encoding="utf-8") as f:
				f.write(final_text)
		except Exception as e:
			log.error(f"CMDReader: Write log failed: {e}")

	def _get_console_text(self, obj):
		if not obj:
			return ""
		try:
			info = obj.makeTextInfo(textInfos.POSITION_FIRST)
			info.expand(textInfos.UNIT_STORY)
			text = info.text
			if not text and hasattr(info, "clipboardText"):
				text = info.clipboardText
			return text or ""
		except Exception as e:
			log.debug(f"CMDReader: Text extraction failed: {e}")
			return ""

	def _monitor_output(self):
		if not self._is_monitoring or not self._current_obj_ref:
			return

		obj = self._current_obj_ref()
		if not obj or not self._is_cmd_window(obj):
			return

		raw_text = self._get_console_text(obj)
		if not raw_text or raw_text == self._last_raw_text:
			core.callLater(800, self._monitor_output)
			return

		threading.Thread(target=self._process_text_async, args=(raw_text,), daemon=True).start()

	def _process_text_async(self, raw_text):
		with self._lock:
			clean_raw = self._clean_line_formatting(raw_text)
			lines = [line for line in clean_raw.splitlines() if line.strip()]
			new_lines_count = len(lines)
			
			if new_lines_count > self._last_processed_line_count:
				new_content = lines[self._last_processed_line_count:]
				core.callLater(0, self._dispatch_speech, new_content)

			self._last_processed_line_count = new_lines_count
			self._last_raw_text = raw_text
			self._write_log(raw_text)
			
			self._shadow_records = lines
			self._current_line_index = len(self._shadow_records) - 1
		
		core.callLater(800, self._monitor_output)

	def _dispatch_speech(self, new_content):
		if not self._is_monitoring:
			return
		for line in new_content:
			if self._prompt_regex.match(line):
				if self._command_running:
					speech.speakText(_("Command Finished"))
					winsound.Beep(800, 100)
					self._command_running = False
			else:
				self._command_running = True
				if self._filter_noise(line):
					speech.speakText(line)
					if any(err in line.lower() for err in self._error_keywords):
						winsound.Beep(440, 100)

	def event_gainFocus(self, obj, nextHandler):
		if self._is_cmd_window(obj):
			self._is_monitoring = True
			self._current_obj_ref = weakref.ref(obj)
			self._last_raw_text = ""
			self._last_processed_line_count = 0
			core.callLater(400, self._monitor_output)
		nextHandler()

	def event_loseFocus(self, obj, nextHandler):
		self._is_monitoring = False
		self._current_obj_ref = None
		nextHandler()

	@scriptHandler.script(
		description=_("Shadow Scroll Up: Reads CMD history lines (Control+Alt+Up)"),
		gesture="kb:control+alt+upArrow"
	)
	def script_shadowUp(self, gesture):
		obj = api.getFocusObject()
		if not self._is_cmd_window(obj):
			ui.message(_("Not in Command Prompt"))
			return
		if self._current_line_index > 0:
			self._current_line_index -= 1
			if 0 <= self._current_line_index < len(self._shadow_records):
				speech.speakText(self._shadow_records[self._current_line_index])
		else:
			ui.message(_("Top"))

	@scriptHandler.script(
		description=_("Shadow Scroll Down: Reads CMD history lines (Control+Alt+Down)"),
		gesture="kb:control+alt+downArrow"
	)
	def script_shadowDown(self, gesture):
		obj = api.getFocusObject()
		if not self._is_cmd_window(obj):
			ui.message(_("Not in Command Prompt"))
			return
		if self._current_line_index < len(self._shadow_records) - 1:
			self._current_line_index += 1
			if 0 <= self._current_line_index < len(self._shadow_records):
				speech.speakText(self._shadow_records[self._current_line_index])
		else:
			ui.message(_("Bottom"))

	@scriptHandler.script(
		description=_("Open CMDReader Log File in Text Editor"),
		gesture="kb:control+alt+l"
	)
	def script_openLogFile(self, gesture):
		if os.path.exists(self.log_path):
			ui.message(_("Opening CMDReader log"))
			os.startfile(self.log_path)
		else:
			ui.message(_("Log file not found"))

	def terminate(self):
		self._is_monitoring = False
		self._current_obj_ref = None
		self._save_history()
		self._clear_log()
		super().terminate()