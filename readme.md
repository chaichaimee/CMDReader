![NVDA Logo](https://www.nvaccess.org/files/nvda/documentation/userGuide/images/nvda.ico)

# CMDReader

Hear every line your terminal prints, the moment it appears.

**author:** chai chaimee

**url:** https://github.com/chaichaimee/CMDReader

## Introduction

CMDReader makes working in the terminal fast and comfortable. It automatically reads new output aloud in Command Prompt, PowerShell, and Windows Terminal as soon as it appears, so you never have to hunt through the window to find out what a command printed.

It also tells you when a command has finished, warns you with a distinct sound when an error appears, and lets you step back through the console output one line at a time with the Up and Down arrow keys. A dedicated settings panel lets you control sounds, privacy, and the words that count as errors.

## Hot Keys

**Control+Alt+L**

- Single Tap : Toggle line review (Up and Down arrows read the console output one line at a time)
- Double Tap : Open the CMDReader log file
- Triple Tap : Open CMDReader settings

This hotkey works only while a console window is focused. In any other application the keystroke is passed through unchanged.

## Features

### Supported Terminals

CMDReader works in Command Prompt, PowerShell (including PowerShell 7), and Windows Terminal.

### Real-Time Output Reading

Whenever new lines appear in the console, CMDReader speaks them automatically. The text that was already on the screen when you opened or switched to the window is treated as a starting point and is not read again, so you only hear what is new.

Example: you type *ping localhost* and press Enter. Each result line is spoken as it is printed.

Blank lines and decorative separator lines made of characters such as = - _ * # are skipped, and the command prompt line itself is not read out as output.

### Sound and Voice Alerts

CMDReader uses three short sounds to keep you informed without extra speech:

- **Window Ready** : a beep that plays once the console has been prepared and CMDReader has started watching it.
- **Command Finished** : when output has been printed and the prompt returns, NVDA says "Command Finished" and a beep plays.
- **Command Error** : a lower beep plays after a line that contains one of your error keywords has been read.

All three beeps can be switched off together with the sound option in settings. The spoken "Command Finished" message stays active.

### Error Detection

Every new line is compared, ignoring upper and lower case, with a list of error keywords. When a match is found, the line is read and the error beep sounds.

The default keywords are: is not recognized as an internal or external command, is not recognized as the name of a cmdlet, access denied, access is denied, permission denied, error 404, fatal error, failed to, exception occurred, cannot find path.

Example: typing a command that does not exist produces "is not recognized as an internal or external command", so you hear the message followed by the error beep.

### Line Review with the Arrow Keys

Line review lets you move through everything the console has printed, one line at a time, without touching the console itself.

- **Up Arrow** : read the previous line.
- **Down Arrow** : read the next line.

When you reach the first line NVDA says "Top", and at the last line it says "Bottom". If nothing has been recorded yet, you hear "No history available".

How to use it, step by step:

1. Focus a Command Prompt, PowerShell, or Windows Terminal window.
2. Press Control+Alt+L once. NVDA says "Line review on". Reading starts from the last line of the output.
3. Press Up Arrow to move back through the output, one line per press, and Down Arrow to move forward.
4. When you want the arrow keys to behave normally again, for example to recall earlier commands, press Control+Alt+L once more. NVDA says "Line review off".

Line review is active only inside a console window. When you switch to another application the arrow keys return to normal automatically.

By default, line review starts automatically each time you move from another application into a console window. This can be changed in settings. If line review is disabled in settings, a single tap announces "Line review is disabled in settings".

### Log Files

CMDReader keeps a plain text copy of the current console output so you can open it in your default text editor and read it at your own pace. A separate file is used for each kind of terminal: CMDReader_CMD.txt for Command Prompt, CMDReader_PowerShell.txt for PowerShell, and CMDReader_Terminal.txt for other terminals.

The log contains the output of your session without the prompt lines and without blank or separator lines. The files are stored in the ChaiChaimee\CMDReader folder inside your NVDA configuration folder, and they are emptied when NVDA starts and when it exits.

How to open the log, step by step:

1. Run your commands in the console as usual.
2. Press Control+Alt+L twice.
3. NVDA says "Opening CMDReader log" and the file opens in your default application. NVDA keeps working while the file opens.

If the file does not exist yet you hear "Log file not found".

### Settings Panel

Open NVDA settings and choose the CMDReader category, or press Control+Alt+L three times inside a console. The panel contains these options:

- **Strict Privacy Mode (Disable writing logs to disk)** : stops CMDReader from writing any log file.
- **Play indicator sounds (Ready, Finished, Error)** : turns the three beeps on or off.
- **Allow line review with the Up and Down arrow keys** : enables or disables line review altogether.
- **Start line review automatically when a console window gets focus** : controls whether line review turns on by itself when you enter a console.
- **Error keywords (comma separated)** : the list of phrases that trigger the error beep.

Changes are applied when you confirm the settings dialog. The command used to open the log and settings can also be reassigned in NVDA's Input Gestures dialog under the CMDReader category.

### Custom Error Keywords

You decide which phrases are treated as errors.

1. Press Control+Alt+L three times in a console, or open NVDA settings and select CMDReader.
2. Go to the "Error keywords (comma separated)" field.
3. Add, change, or remove phrases, separating each one with a comma. For example: access denied, timed out, build failed
4. Press OK to save.

From then on, any new line containing one of your phrases is read and followed by the error beep.

### Strict Privacy Mode

If you work with sensitive information in the terminal, Strict Privacy Mode makes sure nothing is written to disk.

1. Open NVDA settings and select the CMDReader category.
2. Check "Strict Privacy Mode (Disable writing logs to disk)".
3. Press OK.

While this mode is on, CMDReader writes no log files, existing log files are cleared when NVDA starts, and double tapping Control+Alt+L announces "Logging is disabled in Strict Privacy Mode". Reading output aloud and line review continue to work normally.

### Session History in Memory

The history used by line review is kept only in memory while NVDA is running. CMDReader remembers up to 15 console windows at the same time and discards the oldest one beyond that. Older history files from previous versions of the add-on are deleted automatically, and log files are cleared when NVDA exits.

## Support Me

If this tool has made your life easier, consider fueling the next update with a small donation.

[![Support me](https://img.shields.io/badge/Donate-Support%20Me-blue?style=for-the-badge&logo=stripe)](https://buy.stripe.com/dRm9AU1xQ3Ds22N6VK1VK01)

Your support means the world. Let's build something great together

© 2026 Chai Chaimee NVDA Add-on Released under GNU GPL
