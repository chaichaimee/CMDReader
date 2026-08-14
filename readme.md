<p align="center">
  <img src="https://www.nvaccess.org/wp-content/uploads/2015/10/NVDA_logo_standard_transparent.png" alt="NVDA Logo" width="200">
</p>

# CMDReader

<p align="center"><em>Command Line Accessibility, Redefined.</em></p>

<p align="center">
  <strong>Author:</strong> chai chaimee<br>
  <strong>URL:</strong> <a href="https://github.com/chaichaimee/CMDReader">github.com/chaichaimee/CMDReader</a>
</p>

---

CMDReader is an NVDA add‑on that automatically speaks every new line that appears in Command Prompt, PowerShell, or Windows Terminal windows. It transforms the command line into a fully audible experience: new output is read aloud as it arrives, distinct beeps tell you when the terminal is ready, when a command finishes, or when an error occurs, and you can scroll back through the spoken history using simple keyboard shortcuts. Beyond real‑time speech, CMDReader saves a persistent history of each session and keeps separate log files for CMD and PowerShell, so your work is always tracked and never lost—even after you restart NVDA or close the terminal window.

## Features

CMDReader is packed with practical tools designed specifically for blind and low‑vision command‑line users. Here is a complete tour of what it offers:

### Automatic Speech of New Console Output

Whenever a new line appears in the focused terminal, CMDReader speaks it immediately. You do not need to move the review cursor, press a screen‑read command, or do anything manually—the add‑on works silently in the background and reads the output as it is generated. It intelligently skips empty lines, prompt lines (such as `C:\>` or `PS C:\>`), and visual separators like dashed lines, so you hear only the meaningful content. This keeps you continuously informed without flooding you with noise.

### Distinct Audio Notifications

Three different beep tones give you critical state information at a glance (or rather, a listen):

* **Window Ready Tone** (600 Hz, 80 ms) — Played when you first focus a terminal and CMDReader has finished capturing the existing screen content. This tells you that the add‑on is now active and ready to monitor new output.
* **Command Finished Tone** (800 Hz, 100 ms) — Played whenever the prompt reappears after a command, indicating that the previous command has completed execution. This is invaluable when running long processes, as you can hear the exact moment they finish without constantly checking the screen.
* **Error Tone** (440 Hz, 100 ms) — Played when CMDReader detects common error keywords in the output, such as *"access denied"*, *"is not recognized"*, *"failed to"*, or *"exception occurred"*. This immediate audible alert lets you stop and investigate as soon as something goes wrong, saving time and preventing further mistakes.

### Shadow History Scrolling (Control+Alt+Up/Down)

One of the most powerful features is the ability to review previously spoken lines without having to re‑run commands or use NVDA’s review cursor.

* Press **Control+Alt+UpArrow** to move up through the history of lines from the current session. Each press reads the previous line aloud.
* Press **Control+Alt+DownArrow** to move back down toward the most recent output.
* When you reach the top or bottom, you will hear a message saying *"Top"* or *"Bottom"*, so you always know where you are in the history.

This shadow history is maintained separately for each terminal window, so switching between different command prompts does not mix up their histories.

### Persistent History Across Sessions

CMDReader saves the last lines of every monitored session into a JSON file (`cmdreader_history.json`) inside your NVDA configuration directory. This means that even if you close the terminal or restart NVDA, your history remains intact. When you come back to a terminal window, CMDReader restores the shadow history, so you can still scroll back through lines from your previous work. This is especially helpful for long debugging sessions or when you need to recall a command result from earlier in the day.

### Separate Log Files for Each Shell

Instead of using a single shared log file, CMDReader keeps distinct logs for different terminal types:

* **CMDReader_CMD.txt** — for classic Command Prompt sessions.
* **CMDReader_PowerShell.txt** — for PowerShell and pwsh sessions.
* **CMDReader_Terminal.txt** — for other terminal windows (such as Git Bash or generic console hosts).

This separation prevents confusion when you switch between shells frequently. Each log file contains only the filtered, clean output from that specific environment, making it easy to review the exact commands and responses you issued.

### Quick Log Access (Control+Alt+L)

Pressing **Control+Alt+L** instantly opens the log file corresponding to the currently focused terminal in your default text editor. You do not need to browse through folders or guess which log belongs to which shell—CMDReader detects the correct file and opens it for you. This is perfect for copying error messages, sharing logs with colleagues, or performing a detailed manual review of everything that happened in that session.

### Smart Prompt and Noise Filtering

CMDReader does not just read everything blindly. It uses regular expressions to identify and skip prompt lines (e.g., `C:\Users\>` or `PS C:\>`) and also filters out purely decorative lines like sequences of dashes, equals signs, or asterisks. The result is a clean stream of meaningful command output, exactly what you need to hear, without the visual clutter.

### Intelligent Baseline Stabilization

When you first focus a terminal, especially PowerShell, the startup banner may print gradually over a few hundred milliseconds. CMDReader waits for the text to stabilize before capturing the baseline. This ensures that the initial banner is considered "already read" and will not be spoken later as if it were new output. It also prevents false triggers of the "Command Finished" tone right after startup, giving you a smooth and accurate starting point.

## Benefits

CMDReader is not just a collection of features—it directly improves your daily workflow and overall comfort when working at the command line. Here is how it makes a real difference:

* **Dramatically saves time and effort** — Without CMDReader, you would have to manually navigate the screen with NVDA’s review cursor, read lines one by one, and constantly switch between keyboard layouts. With automatic speech, you receive the output in real time, allowing you to stay focused on typing the next command instead of reading the last one.
* **Reduces keystroke fatigue** — The shadow scrolling gestures (`Ctrl+Alt+Up/Down`) replace dozens of navigational keystrokes. You no longer need to press `NVDA+Up` repeatedly or move the cursor to the bottom of the screen. Two simple gestures give you full access to the entire session history.
* **Catches errors instantly** — The distinct error beep acts as an early warning system. Instead of reading through pages of output to find a failure, you are alerted the moment an error keyword appears. This is crucial during automated scripts, builds, or installations where a single unnoticed error could cascade into bigger problems.
* **Improves multitasking and focus** — Because CMDReader speaks output and provides audio cues, you can listen to the terminal while working in other applications. You will know when a long process finishes (by the command‑finished tone) or when an error occurs, so you can switch back to the terminal exactly when needed, without constantly alt‑tabbing to check.
* **Maintains continuity across restarts** — The persistent history and separate log files mean you never lose context. If you need to restart NVDA or close a terminal window, you can pick up exactly where you left off, and the shadow history will still contain the lines from before. This is a lifesaver when troubleshooting issues that span multiple sessions.
* **Works seamlessly with all Windows terminals** — Whether you use the old console host, Windows Terminal, or even PowerShell ISE, CMDReader adapts to the window class and app name. It does not require per‑terminal configuration; just focus a compatible window and the add‑on starts monitoring immediately.
* **Eliminates guesswork with audio cues** — The three distinct tones (ready, finished, error) give you a clear sense of the terminal’s state. You will never wonder whether a command is still running or whether the prompt has returned—the beeps tell you, allowing you to type the next command with confidence.

## Why Use CMDReader?

The core problem CMDReader solves is the inherent silence and static nature of the command‑line interface for screen‑reader users. When you cannot see the screen, the terminal is just a block of text that changes unpredictably. Relying on NVDA’s review cursor is slow and interrupts your flow: you have to move to the bottom, read line by line, and manually keep track of what is new. Moreover, you have no audible indication of when a command finishes or when an error appears unless you actively scan the output.

CMDReader changes this paradigm by turning the terminal into an active, audible conversation. New output is spoken as it happens, so you never fall behind. Audio tones give you immediate feedback on system state without requiring visual attention. The shadow history and persistent logs let you review past output effortlessly, even after the window has been closed. All of this is packaged in a lightweight, zero‑configuration add‑on that respects your privacy—all data is stored locally in your NVDA configuration folder.

For system administrators, developers, and power users who spend hours at the command line, CMDReader is not just a convenience—it is a productivity multiplier. It reduces cognitive load, prevents missed errors, and makes the terminal feel as responsive and talkative as any graphical application. If you have ever struggled to keep up with a fast‑scrolling build script or wished you could easily review a previous command’s output without retyping it, CMDReader is the tool you have been waiting for.

## Get the Most Out of Your Terminal Today

CMDReader is a free, open‑source NVDA add‑on developed with the input of blind users and accessibility experts. It requires no complicated setup: just install it, restart NVDA, and focus any Command Prompt, PowerShell, or Windows Terminal window. The add‑on will automatically start monitoring, and you will hear the ready tone confirming it is active. From that moment on, every new line is spoken, every command finish is announced, and every error is beeped—giving you complete audio awareness of your command‑line environment.

The developer, Chai Chaimee, has designed CMDReader with careful attention to real‑world workflows, including migration from older configuration paths and robust handling of different terminal types. It is regularly maintained and fully compatible with the latest versions of NVDA and Windows.

Whether you are managing servers, writing code, automating tasks, or simply navigating file systems, CMDReader makes the command line a far more accessible and enjoyable place to work. Download it from the official NVDA add‑on repository, install it, and give your terminal a voice. You will wonder how you ever managed without it.

## Support Me

If this tool has made your life easier, consider fueling the next update with a small donation.

[![Support me](https://img.shields.io/badge/Donate-Support%20Me-blue?style=for-the-badge&logo=stripe)](https://buy.stripe.com/dRm9AU1xQ3Ds22N6VK1VK01)

Your support means the world. Let's build something great together.

---

&copy; 2026 Chai Chaimee NVDA Add-on. Released under GPL.