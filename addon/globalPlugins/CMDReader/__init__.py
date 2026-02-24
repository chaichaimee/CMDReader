# __init__.py
# Copyright (C) 2026 Chai Chaimee
# Licensed under GNU General Public License. See COPYING.txt for details.

import os
import re
import winsound
import globalVars
import addonHandler
import globalPluginHandler
import api
import ui
import textInfos
import speech
import scriptHandler
import core
import config
from keyboardHandler import KeyboardInputGesture
from logHandler import log

# Initialize translation
addonHandler.initTranslation()

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    scriptCategory = _("CMDReader")

    # Regex to match a Windows command prompt line (e.g., "D:\>", "E:\nvda 2025\2025>")
    _prompt_regex = re.compile(r'^[A-Za-z]:\\.*>\s*$|^>\s*$')
    
    # Error keywords to trigger alert beep
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

        # Set log path according to Chai Rules and NVDA standards
        config_dir = globalVars.appArgs.configPath or config.getAppDataPath()
        self.log_path = os.path.join(config_dir, "CMDReader.txt")

        # Clear log file when plugin starts
        core.callLater(500, self._clear_log)

    def _is_cmd_window(self, obj):
        """Strictly identify a Command Prompt window by process name only."""
        if not obj:
            return False
        try:
            if obj.appModule and obj.appModule.appName.lower() in ["cmd", "powershell", "pwsh"]:
                return True
        except AttributeError:
            pass
        return False

    def _clear_log(self):
        try:
            with open(self.log_path, "w", encoding="utf-8") as f:
                f.write("")
        except Exception as e:
            log.debug(f"CMDReader: Clear log failed: {e}")

    def _clean_line_formatting(self, text):
        """Removes trailing whitespace from each line and strips leading/trailing empty lines."""
        if not text:
            return ""
        lines = []
        for line in text.splitlines():
            # rstrip() removes spaces at the end of the line (fixes the padding issue)
            cleaned_line = line.rstrip()
            if cleaned_line:
                lines.append(cleaned_line)
        return "\n".join(lines)

    def _trim_to_first_prompt(self, text):
        if not text:
            return text
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if self._prompt_regex.search(line):
                return "\n".join(lines[i:])
        return text

    def _filter_noise(self, line):
        """Smart Noise Filtering: Skip decorative lines."""
        clean = line.strip()
        if not clean or re.match(r'^[=\-_*#]{3,}$', clean):
            return False
        return True

    def _write_log(self, text):
        trimmed = self._trim_to_first_prompt(text)
        # Apply strict rstrip and basic cleaning
        clean_data = self._clean_line_formatting(trimmed)
        lines = clean_data.splitlines()
        # Filter out prompts and noise for the backup log
        filtered = [line for line in lines if not self._prompt_regex.match(line) and self._filter_noise(line)]
        final_text = "\n".join(filtered)
        try:
            with open(self.log_path, "w", encoding="utf-8") as f:
                f.write(final_text)
        except Exception as e:
            log.debug(f"CMDReader: Write log failed: {e}")

    def _get_console_text(self, obj):
        try:
            info = obj.makeTextInfo(textInfos.POSITION_FIRST)
            info.expand(textInfos.UNIT_STORY)
            return info.clipboardText or ""
        except:
            return ""

    def _monitor_output(self, obj):
        """Monitor new output, check errors, and detect process completion."""
        if not self._is_monitoring or not self._is_cmd_window(obj):
            return

        raw_text = self._get_console_text(obj)
        if raw_text == self._last_raw_text:
            core.callLater(1000, self._monitor_output, obj)
            return

        # Prepare cleaned lines for processing
        clean_raw = self._clean_line_formatting(raw_text)
        lines = [line for line in clean_raw.splitlines() if line.strip()]
        new_lines_count = len(lines)
        
        if new_lines_count > self._last_processed_line_count:
            new_content = lines[self._last_processed_line_count:]
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

        self._last_processed_line_count = new_lines_count
        self._last_raw_text = raw_text
        self._write_log(raw_text)
        
        self._shadow_records = lines
        self._current_line_index = len(self._shadow_records) - 1
        
        core.callLater(1000, self._monitor_output, obj)

    def event_gainFocus(self, obj, nextHandler):
        if self._is_cmd_window(obj):
            self._is_monitoring = True
            core.callLater(500, self._monitor_output, obj)
        nextHandler()

    def event_loseFocus(self, obj, nextHandler):
        self._is_monitoring = False
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
        self._clear_log()
        super().terminate()