# cmdCore.py

import os
import re
import shutil
import winsound
import weakref
import threading
import winUser
import addonHandler
import globalPluginHandler
import api
import ui
import textInfos
import speech
import scriptHandler
import core
import config
import wx
import gui
from gui.settingsDialogs import SettingsPanel, NVDASettingsDialog
from comtypes import COMError
from logHandler import log

USER_CONFIG_PATH = config.getUserDefaultConfigPath()
_ADDON_ROOT = os.path.join(USER_CONFIG_PATH, "ChaiChaimee")
ADDON_DATA_DIR = os.path.join(_ADDON_ROOT, "CMDReader")

HISTORY_FILE_NAME = "cmdreader_history.json"
LEGACY_SHARED_LOG = "CMDReader.txt"

LOG_FILENAMES = {
    "cmd": "CMDReader_CMD.txt",
    "powershell": "CMDReader_PowerShell.txt",
    "generic": "CMDReader_Terminal.txt",
}

WINDOW_READY_TONE = (600, 80)
COMMAND_FINISHED_TONE = (800, 100)
COMMAND_ERROR_TONE = (440, 100)

MAX_TRACKED_WINDOWS = 15
BASELINE_POLL_INTERVAL_MS = 300
MAX_BASELINE_ATTEMPTS = 6

REVIEW_KEY_BINDINGS = {
    "kb:upArrow": "reviewLineUp",
    "kb:downArrow": "reviewLineDown",
}

TAP_WINDOW_MS = 350


def getTapAction(tapCount):
    if tapCount <= 0:
        return None
    if tapCount == 1:
        return "toggleReview"
    if tapCount == 2:
        return "openLog"
    return "openSettings"

confspec = {
    "CMDReader": {
        "strictPrivacyMode": "boolean(default=False)",
        "playSounds": "boolean(default=True)",
        "arrowKeyReview": "boolean(default=True)",
        "arrowKeyReviewAutoStart": "boolean(default=True)",
        "errorKeywords": "string(default='is not recognized as an internal or external command, is not recognized as the name of a cmdlet, access denied, access is denied, permission denied, error 404, fatal error, failed to, exception occurred, cannot find path')"
    }
}
config.conf.spec.update(confspec)


class CMDReaderSettingsPanel(SettingsPanel):
    title = _("CMDReader")

    def makeSettings(self, settingsSizer):
        sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
        
        self.privacyCheckbox = sHelper.addItem(
            wx.CheckBox(self, label=_("Strict Privacy Mode (Disable writing logs to disk)"))
        )
        self.privacyCheckbox.SetValue(config.conf["CMDReader"]["strictPrivacyMode"])

        self.soundCheckbox = sHelper.addItem(
            wx.CheckBox(self, label=_("Play indicator sounds (Ready, Finished, Error)"))
        )
        self.soundCheckbox.SetValue(config.conf["CMDReader"]["playSounds"])

        self.arrowReviewCheckbox = sHelper.addItem(
            wx.CheckBox(self, label=_("Allow line review with the Up and Down arrow keys (single tap of Control+Alt+L toggles it)"))
        )
        self.arrowReviewCheckbox.SetValue(config.conf["CMDReader"]["arrowKeyReview"])

        self.arrowAutoStartCheckbox = sHelper.addItem(
            wx.CheckBox(self, label=_("Start line review automatically when a console window gets focus"))
        )
        self.arrowAutoStartCheckbox.SetValue(config.conf["CMDReader"]["arrowKeyReviewAutoStart"])

        self.errorKeywordsTextCtrl = sHelper.addLabeledControl(
            _("Error keywords (comma separated):"),
            wx.TextCtrl
        )
        self.errorKeywordsTextCtrl.SetValue(config.conf["CMDReader"]["errorKeywords"])

    def onSave(self):
        config.conf["CMDReader"]["strictPrivacyMode"] = self.privacyCheckbox.GetValue()
        config.conf["CMDReader"]["playSounds"] = self.soundCheckbox.GetValue()
        config.conf["CMDReader"]["arrowKeyReview"] = self.arrowReviewCheckbox.GetValue()
        config.conf["CMDReader"]["arrowKeyReviewAutoStart"] = self.arrowAutoStartCheckbox.GetValue()
        config.conf["CMDReader"]["errorKeywords"] = self.errorKeywordsTextCtrl.GetValue()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    scriptCategory = _("CMDReader")

    _prompt_regex = re.compile(
        r'^[A-Za-z]:\\.*>\s*$'
        r'|^>\s*$'
        r'|^PS\s+[A-Za-z]:\\.*>\s*$'
        r'|^PS\s+.*>\s*$'
        r'|^[A-Za-z0-9_\-]+@[A-Za-z0-9_\-]+:.*[\$\s]*$'
    )

    _prompt_start_regex = re.compile(
        r'^[A-Za-z]:\\[^>]*>'
        r'|^PS\s+[^>]*>'
        r'|^[A-Za-z0-9_\-]+@[A-Za-z0-9_\-]+:'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._window_states = {}
        self._current_hwnd = None
        self._current_obj_ref = None
        self._is_monitoring = False
        self._monitor_epoch = 0
        self._lock = threading.Lock()
        self._shadow_records = []
        self._reviewModeOn = False
        self._tapCount = 0
        self._tapTimer = None
        self._reviewKeysBound = False
        self._focusWasConsole = False

        NVDASettingsDialog.categoryClasses.append(CMDReaderSettingsPanel)

        self._ensure_config_dir()
        self._migrate_and_cleanup()

        if config.conf["CMDReader"]["strictPrivacyMode"]:
            self._clear_log()
        else:
            core.callLater(500, self._clear_log)

    def _ensure_config_dir(self):
        try:
            os.makedirs(ADDON_DATA_DIR, exist_ok=True)
        except OSError as e:
            log.error(f"CMDReader: Directory creation failed: {e}")

    def _migrate_and_cleanup(self):
        history_paths = [
            os.path.join(USER_CONFIG_PATH, HISTORY_FILE_NAME),
            os.path.join(_ADDON_ROOT, HISTORY_FILE_NAME),
            os.path.join(ADDON_DATA_DIR, HISTORY_FILE_NAME)
        ]
        for path in history_paths:
            self._safe_delete(path)

        generic_log_path = self._log_path_for_kind("generic")
        
        legacy_logs = [
            os.path.join(USER_CONFIG_PATH, LEGACY_SHARED_LOG),
            os.path.join(_ADDON_ROOT, LEGACY_SHARED_LOG)
        ]
        for old_log in legacy_logs:
            if os.path.isfile(old_log):
                self._safe_move(old_log, generic_log_path)

        for filename in LOG_FILENAMES.values():
            old_per_shell = os.path.join(_ADDON_ROOT, filename)
            if os.path.isfile(old_per_shell):
                new_per_shell = os.path.join(ADDON_DATA_DIR, filename)
                self._safe_move(old_per_shell, new_per_shell)

        known_logs = set(LOG_FILENAMES.values())
        known_logs.add(LEGACY_SHARED_LOG)
        for dirpath in (USER_CONFIG_PATH, _ADDON_ROOT):
            for fname in known_logs:
                filepath = os.path.join(dirpath, fname)
                self._safe_delete(filepath)

    def _safe_move(self, src, dst):
        try:
            shutil.move(src, dst)
        except OSError as e:
            log.error(f"CMDReader: Failed to move {src} -> {dst}: {e}")

    def _safe_delete(self, target_path):
        try:
            if os.path.isfile(target_path):
                os.remove(target_path)
        except OSError:
            pass

    def _get_hwnd(self, obj):
        if not obj:
            return None
        try:
            return getattr(obj, "windowHandle", None)
        except (AttributeError, RuntimeError, COMError):
            return None

    def _is_cmd_window(self, obj):
        if not obj:
            return False
        try:
            hwnd = getattr(obj, "windowHandle", None)
            if hwnd:
                window_class = winUser.getClassName(hwnd).lower()
                if "consolewindowclass" in window_class or "cascadia" in window_class:
                    return True
            app_module = obj.appModule
            if app_module:
                app_name = app_module.appName.lower()
                if app_name in ("cmd", "powershell", "pwsh", "windowsterminal"):
                    return True
        except (AttributeError, RuntimeError, COMError):
            pass
        return False

    def _log_path_for_kind(self, kind):
        filename = LOG_FILENAMES.get(kind, LOG_FILENAMES["generic"])
        return os.path.join(ADDON_DATA_DIR, filename)

    def _detect_shell_kind(self, appName, rawText=""):
        appName = (appName or "").lower()
        if appName in ("powershell", "pwsh"):
            return "powershell"
        if appName == "cmd":
            return "cmd"
        if rawText and re.search(r'^PS\s+[A-Za-z]:\\', rawText, re.MULTILINE):
            return "powershell"
        if appName:
            return "cmd"
        return "generic"

    def _clear_log(self):
        for kind in LOG_FILENAMES:
            path = self._log_path_for_kind(kind)
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write("")
            except OSError as e:
                log.error(f"CMDReader: Clear log failed ({kind}): {e}")

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
            if self._prompt_start_regex.match(line):
                return "\n".join(lines[i:])
        return text

    def _filter_noise(self, line):
        clean = line.strip()
        if not clean or re.match(r'^[=\-_*#]{3,}$', clean):
            return False
        return True

    def _write_log(self, text, hwnd):
        if config.conf["CMDReader"]["strictPrivacyMode"]:
            return

        state = self._window_states.get(hwnd)
        shell_kind = state.get("shell_kind", "generic") if state else "generic"
        log_path = self._log_path_for_kind(shell_kind)

        trimmed = self._trim_to_first_prompt(text)
        clean_data = self._clean_line_formatting(trimmed)
        lines = clean_data.splitlines()
        filtered = [line for line in lines if not self._prompt_regex.match(line) and self._filter_noise(line)]
        final_text = "\n".join(filtered)
        
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(final_text)
        except OSError as e:
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
        except (RuntimeError, COMError) as e:
            log.debug(f"CMDReader: Text extraction failed: {e}")
            return ""

    def _prune_window_states(self):
        while len(self._window_states) > MAX_TRACKED_WINDOWS:
            oldest_hwnd = next(iter(self._window_states))
            del self._window_states[oldest_hwnd]

    def _startMonitoringSession(self, epoch, hwnd):
        if epoch != self._monitor_epoch or not self._is_monitoring:
            return
        obj = self._current_obj_ref() if self._current_obj_ref else None
        if not obj or not self._is_cmd_window(obj):
            return

        isNewWindow = hwnd is None or hwnd not in self._window_states
        if isNewWindow:
            rawText = self._get_console_text(obj)
            core.callLater(BASELINE_POLL_INTERVAL_MS, self._stabilizeBaseline, epoch, hwnd, rawText, 0)
        else:
            self._monitor_output(epoch)

    def _stabilizeBaseline(self, epoch, hwnd, previousText, attempt):
        if epoch != self._monitor_epoch or not self._is_monitoring:
            return
        obj = self._current_obj_ref() if self._current_obj_ref else None
        if not obj or not self._is_cmd_window(obj):
            return

        currentText = self._get_console_text(obj)
        isStable = currentText == previousText
        
        if isStable or attempt >= MAX_BASELINE_ATTEMPTS:
            try:
                appName = obj.appModule.appName if obj.appModule else ""
            except (AttributeError, RuntimeError, COMError):
                appName = ""
            
            threading.Thread(
                target=self._finalizeBaseline,
                args=(hwnd, currentText, appName, epoch),
                daemon=True
            ).start()
            return

        core.callLater(BASELINE_POLL_INTERVAL_MS, self._stabilizeBaseline, epoch, hwnd, currentText, attempt + 1)

    def _finalizeBaseline(self, hwnd, rawText, appName, epoch):
        with self._lock:
            clean_raw = self._clean_line_formatting(rawText)
            lines = [line for line in clean_raw.splitlines() if line.strip()]
            self._window_states[hwnd] = {
                "last_raw_text": rawText,
                "last_processed_line_count": len(lines),
                "command_running": False,
                "shadow_records": lines,
                "current_line_index": len(lines) - 1,
                "shell_kind": self._detect_shell_kind(appName, rawText),
            }
            self._shadow_records = lines
            self._prune_window_states()

        core.callLater(0, self._onWindowReady, epoch)
        core.callLater(800, self._monitor_output, epoch)

    def _onWindowReady(self, epoch):
        if epoch != self._monitor_epoch or not self._is_monitoring:
            return
        if config.conf["CMDReader"]["playSounds"]:
            winsound.Beep(*WINDOW_READY_TONE)

    def _monitor_output(self, epoch):
        if epoch != self._monitor_epoch or not self._is_monitoring or not self._current_obj_ref:
            return

        obj = self._current_obj_ref()
        if not obj or not self._is_cmd_window(obj):
            return

        hwnd = self._current_hwnd
        state = self._window_states.get(hwnd)
        if state is None:
            return

        raw_text = self._get_console_text(obj)
        if not raw_text or raw_text == state["last_raw_text"]:
            core.callLater(800, self._monitor_output, epoch)
            return

        threading.Thread(target=self._process_text_async, args=(raw_text, hwnd, epoch), daemon=True).start()

    def _process_text_async(self, raw_text, hwnd, epoch):
        with self._lock:
            state = self._window_states.get(hwnd)
            if state is None:
                return

            clean_raw = self._clean_line_formatting(raw_text)
            lines = [line for line in clean_raw.splitlines() if line.strip()]
            new_lines_count = len(lines)
            previous_count = state["last_processed_line_count"]

            if new_lines_count > previous_count:
                new_content = lines[previous_count:]
                core.callLater(0, self._dispatch_speech, new_content, hwnd, epoch)

            state["last_processed_line_count"] = new_lines_count
            state["last_raw_text"] = raw_text
            state["shadow_records"] = lines
            state["current_line_index"] = len(lines) - 1

            self._shadow_records = lines
            self._write_log(raw_text, hwnd)

        if epoch == self._monitor_epoch and self._is_monitoring:
            core.callLater(800, self._monitor_output, epoch)

    def _dispatch_speech(self, new_content, hwnd, epoch):
        if epoch != self._monitor_epoch or not self._is_monitoring:
            return
        state = self._window_states.get(hwnd)
        if state is None:
            return

        raw_keywords = config.conf["CMDReader"]["errorKeywords"]
        custom_errors = [k.strip().lower() for k in raw_keywords.split(",") if k.strip()]

        for line in new_content:
            if self._prompt_regex.match(line):
                if state["command_running"]:
                    speech.speakText(_("Command Finished"))
                    if config.conf["CMDReader"]["playSounds"]:
                        winsound.Beep(*COMMAND_FINISHED_TONE)
                    state["command_running"] = False
            else:
                state["command_running"] = True
                if self._filter_noise(line):
                    speech.speakText(line)
                    if any(err in line.lower() for err in custom_errors):
                        if config.conf["CMDReader"]["playSounds"]:
                            winsound.Beep(*COMMAND_ERROR_TONE)

    def _bindReviewKeys(self):
        if self._reviewKeysBound:
            return
        self.bindGestures(REVIEW_KEY_BINDINGS)
        self._reviewKeysBound = True

    def _unbindReviewKeys(self):
        if not self._reviewKeysBound:
            return
        for gestureId in REVIEW_KEY_BINDINGS:
            try:
                self.removeGestureBinding(gestureId)
            except LookupError:
                log.debug(f"CMDReader: Review key {gestureId} was not bound")
        self._reviewKeysBound = False

    def _setReviewMode(self, isOn):
        self._reviewModeOn = isOn
        if isOn:
            self._bindReviewKeys()
        else:
            self._unbindReviewKeys()

    def _restoreReviewModeOnFocus(self, isEntering):
        if not config.conf["CMDReader"]["arrowKeyReview"]:
            self._setReviewMode(False)
            return
        if isEntering and config.conf["CMDReader"]["arrowKeyReviewAutoStart"]:
            self._reviewModeOn = True
        if self._reviewModeOn:
            self._bindReviewKeys()

    def _stepShadowLine(self, step):
        obj = api.getFocusObject()
        if not self._is_cmd_window(obj):
            ui.message(_("Not in Command Prompt"))
            return
        hwnd = self._get_hwnd(obj)
        state = self._window_states.get(hwnd)
        if not state or not state["shadow_records"]:
            ui.message(_("No history available"))
            return
        records = state["shadow_records"]
        currentIndex = min(state["current_line_index"], len(records) - 1)
        newIndex = currentIndex + step
        if newIndex < 0:
            ui.message(_("Top"))
            return
        if newIndex >= len(records):
            ui.message(_("Bottom"))
            return
        state["current_line_index"] = newIndex
        speech.speakText(records[newIndex])

    def event_gainFocus(self, obj, nextHandler):
        isConsole = self._is_cmd_window(obj)
        if isConsole:
            hwnd = self._get_hwnd(obj)
            self._monitor_epoch += 1
            currentEpoch = self._monitor_epoch
            self._is_monitoring = True
            self._current_obj_ref = weakref.ref(obj)
            self._current_hwnd = hwnd
            core.callLater(400, self._startMonitoringSession, currentEpoch, hwnd)
            self._restoreReviewModeOnFocus(not self._focusWasConsole)
        else:
            self._setReviewMode(False)
        self._focusWasConsole = isConsole
        nextHandler()

    def event_loseFocus(self, obj, nextHandler):
        self._is_monitoring = False
        self._current_obj_ref = None
        self._unbindReviewKeys()
        nextHandler()

    def script_reviewLineUp(self, gesture):
        self._stepShadowLine(-1)

    def script_reviewLineDown(self, gesture):
        self._stepShadowLine(1)

    @scriptHandler.script(
        description=_(
            "Single tap: toggle line review (Up and Down arrows read the console output one line at a time). "
            "Double tap: open the CMDReader log file. Triple tap: open CMDReader settings"
        ),
        gesture="kb:control+alt+l"
    )
    def script_cmdReaderMultiTap(self, gesture):
        if not self._is_cmd_window(api.getFocusObject()):
            gesture.send()
            return
        if self._tapTimer is not None:
            self._tapTimer.Stop()
        self._tapCount += 1
        self._tapTimer = core.callLater(TAP_WINDOW_MS, self._dispatchTapAction)

    def _dispatchTapAction(self):
        action = getTapAction(self._tapCount)
        self._tapCount = 0
        self._tapTimer = None
        obj = api.getFocusObject()
        if not self._is_cmd_window(obj):
            return
        if action == "toggleReview":
            self._toggleLineReview(obj)
        elif action == "openLog":
            self._openLogFile(obj)
        elif action == "openSettings":
            wx.CallAfter(self._openSettingsPanel)

    def _toggleLineReview(self, obj):
        if not config.conf["CMDReader"]["arrowKeyReview"]:
            ui.message(_("Line review is disabled in settings"))
            return
        if self._reviewModeOn:
            self._setReviewMode(False)
            ui.message(_("Line review off"))
            return
        state = self._window_states.get(self._get_hwnd(obj))
        if state and state["shadow_records"]:
            state["current_line_index"] = len(state["shadow_records"]) - 1
        self._setReviewMode(True)
        ui.message(_("Line review on"))

    def _openSettingsPanel(self):
        try:
            gui.mainFrame.popupSettingsDialog(NVDASettingsDialog, CMDReaderSettingsPanel)
        except Exception as e:
            log.error(f"CMDReader: Open settings failed: {e}")

    def _openLogFile(self, obj):
        if config.conf["CMDReader"]["strictPrivacyMode"]:
            ui.message(_("Logging is disabled in Strict Privacy Mode"))
            return

        hwnd = self._get_hwnd(obj)
        state = self._window_states.get(hwnd)
        if state:
            shell_kind = state.get("shell_kind", "generic")
        else:
            try:
                appName = obj.appModule.appName if obj.appModule else ""
            except (AttributeError, RuntimeError, COMError):
                appName = ""
            shell_kind = self._detect_shell_kind(appName)

        log_path = self._log_path_for_kind(shell_kind)
        if os.path.exists(log_path):
            ui.message(_("Opening CMDReader log"))
            threading.Thread(target=self._startLogFile, args=(log_path,), daemon=True).start()
        else:
            ui.message(_("Log file not found"))

    def _startLogFile(self, log_path):
        try:
            os.startfile(log_path)
        except OSError as e:
            log.error(f"CMDReader: Open log failed: {e}")
            wx.CallAfter(ui.message, _("Could not open CMDReader log"))

    def terminate(self):
        self._is_monitoring = False
        self._current_obj_ref = None
        if self._tapTimer is not None:
            self._tapTimer.Stop()
            self._tapTimer = None
        self._setReviewMode(False)
        self._window_states.clear()
        self._shadow_records.clear()
        
        try:
            NVDASettingsDialog.categoryClasses.remove(CMDReaderSettingsPanel)
        except ValueError:
            pass

        self._clear_log()
        super().terminate()