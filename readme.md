<div align="center">

<img src="https://www.nvaccess.org/wp-content/uploads/2015/10/NVDA_logo_standard_transparent.png" alt="NVDA Logo" width="200">

# CMDReader

*Command Line Accessibility, Redefined.*

<br>

**Author:** chai chaimee  
**URL:** [github.com/chaichaimee/CMDReader](https://github.com/chaichaimee/CMDReader)

</div>

---

<br>

CMDReader is an NVDA add‑on that automatically speaks every new line that appears in Command Prompt, PowerShell, or Windows Terminal windows. It transforms the command line into a fully audible experience: new output is read aloud as it arrives, distinct beeps tell you when the terminal is ready, when a command finishes, or when an error occurs, and you can scroll back through the spoken history using simple keyboard shortcuts. Beyond real‑time speech, CMDReader provides seamless in-session shadow history and highly customizable privacy settings directly within NVDA, ensuring your console data is strictly managed and securely wiped when you are done.

<br><br>

## Features

CMDReader is packed with practical tools designed specifically for blind and low‑vision command‑line users. Here is a complete tour of what it offers:

### Automatic Speech of New Console Output

Whenever a new line appears in the focused terminal, CMDReader speaks it immediately. You do not need to move the review cursor, press a screen‑read command, or do anything manually—the add‑on works silently in the background and reads the output as it is generated. It intelligently skips empty lines, prompt lines (such as `C:\>` or `PS C:\>`), and visual separators like dashed lines, so you hear only the meaningful content. This keeps you continuously informed without flooding you with noise.

### Customizable Settings via NVDA GUI

CMDReader integrates directly into the NVDA preferences menu. Navigate to **NVDA Menu > Preferences > Settings > CMDReader** to fully tailor the add-on to your workflow:

* **Strict Privacy Mode:** When enabled, this completely disables the writing of session logs (.txt files) to your hard drive. All terminal history is kept strictly in-memory (RAM) and vanishes the moment you close NVDA. This is perfect for system administrators handling highly sensitive SSH connections or private server data.
* **Audio Indicator Toggles:** Choose whether to enable or disable the distinct background beeps (Window Ready, Command Finished, and Error detected).
* **Customizable Error Keywords:** You can edit the comma-separated list of words that trigger the error alert. Add specific compiler errors, framework exceptions, or custom script outputs to instantly catch exactly what you are looking for.

### Distinct Audio Notifications

If enabled in settings, three different beep tones give you critical state information at a glance (or rather, a listen):

* **Window Ready Tone** (600 Hz, 80 ms) — Played when you first focus a terminal and CMDReader has finished capturing the existing screen content. This tells you that the add‑on is active and ready.
* **Command Finished Tone** (800 Hz, 100 ms) — Played whenever the prompt reappears after a command, indicating completion. This is invaluable when running long processes.
* **Error Tone** (440 Hz, 100 ms) — Played when CMDReader detects your specified error keywords in the output. This immediate audible alert lets you stop and investigate as soon as something goes wrong.

### Shadow History Scrolling (Control+Alt+Up/Down)

One of the most powerful features is the ability to review previously spoken lines from your current session without having to re‑run commands or use NVDA’s review cursor.

* Press **Control+Alt+UpArrow** to move up through the history of lines. Each press reads the previous line aloud.
* Press **Control+Alt+DownArrow** to move back down toward the most recent output.
* When you reach the top or bottom, you will hear a message saying *"Top"* or *"Bottom"*.

### Strict In-Memory Security & Aggressive Cleanup

Your privacy is paramount. CMDReader stores your shadow scrolling history strictly in your system's RAM (in-memory) during your active session. When you close or restart NVDA, this memory is instantly and permanently wiped. Furthermore, CMDReader performs an aggressive cleanup routine on startup, automatically detecting and deleting any legacy JSON history files (from older add-on versions) or scattered logs, ensuring no sensitive console data is ever left behind on your disk.

### Separate Log Files for Each Shell (Optional)

Unless you have Strict Privacy Mode enabled, CMDReader keeps distinct temporary logs for different terminal types in your NVDA config folder:

* **CMDReader_CMD.txt** — for classic Command Prompt sessions.
* **CMDReader_PowerShell.txt** — for PowerShell and pwsh sessions.
* **CMDReader_Terminal.txt** — for other terminal windows (such as Git Bash).

This separation prevents confusion when you switch between shells frequently. These log files are automatically cleared every time you shut down NVDA.

### Quick Log Access (Control+Alt+L)

Pressing **Control+Alt+L** instantly opens the temporary log file corresponding to the currently focused terminal in your default text editor (provided Strict Privacy Mode is disabled). You do not need to browse through folders—CMDReader detects the correct file and opens it for you. This is perfect for copying error messages or performing a detailed manual review.

### Intelligent Baseline Stabilization

When you first focus a terminal, especially PowerShell, the startup banner may print gradually over a few hundred milliseconds. CMDReader waits for the text to stabilize before capturing the baseline. This ensures that the initial banner is considered "already read" and will not be spoken later, preventing false triggers.

<br><br>

## Benefits

CMDReader is not just a collection of features—it directly improves your daily workflow and overall comfort when working at the command line. Here is how it makes a real difference:

* **Dramatically saves time and effort** — Without CMDReader, you would have to manually navigate the screen with NVDA’s review cursor. With automatic speech, you receive the output in real time, allowing you to stay focused on typing.
* **Reduces keystroke fatigue** — The shadow scrolling gestures (`Ctrl+Alt+Up/Down`) replace dozens of navigational keystrokes. Two simple gestures give you full access to the entire session history.
* **Catches errors instantly** — The distinct error beep acts as an early warning system. Instead of reading through pages of output to find a failure, you are alerted the moment an error keyword appears.
* **Improves multitasking and focus** — Because CMDReader speaks output and provides audio cues, you can listen to the terminal while working in other applications. You will know exactly when a long process finishes.
* **Maximum Privacy Control** — With the strict in-memory architecture and GUI-toggled Strict Privacy Mode, system administrators and developers can work with confidential server data, API keys, and secure connections knowing absolutely nothing is being secretly logged to the hard drive.
* **Works seamlessly with all Windows terminals** — Whether you use the old console host, Windows Terminal, or even PowerShell ISE, CMDReader adapts to the window class and app name automatically.

<br><br>

## Why Use CMDReader?

The core problem CMDReader solves is the inherent silence and static nature of the command‑line interface for screen‑reader users. When you cannot see the screen, the terminal is just a block of text that changes unpredictably. Relying on NVDA’s review cursor is slow and interrupts your flow.

CMDReader changes this paradigm by turning the terminal into an active, audible conversation. New output is spoken as it happens, so you never fall behind. Audio tones give you immediate feedback on system state. The shadow history lets you review past output effortlessly during your active session. All of this is packaged in a lightweight, highly secure add‑on that gives you absolute control over what is read, what beeps, and what is saved.

For system administrators, developers, and power users who spend hours at the command line, CMDReader is not just a convenience—it is a productivity multiplier. It reduces cognitive load, prevents missed errors, and makes the terminal feel responsive and intuitive.

<br><br>

## Get the Most Out of Your Terminal Today

CMDReader is a free, open‑source NVDA add‑on developed with the input of blind users and accessibility experts. It requires no complicated setup: just install it, and focus any Command Prompt, PowerShell, or Windows Terminal window. The add‑on will automatically start monitoring. Explore the NVDA Settings menu to configure your privacy mode, custom error triggers, and audio alerts.

The developer, Chai Chaimee, has designed CMDReader with careful attention to real‑world workflows, enterprise-grade security practices, and robust handling of different terminal types. It is regularly maintained and fully compatible with the latest versions of NVDA and Windows.

Whether you are managing servers, writing code, automating tasks, or simply navigating file systems, CMDReader makes the command line a far more accessible and secure place to work. Download it from the official NVDA add‑on repository, install it, and give your terminal a voice.

<br><br>

## Support Me

If this tool has made your life easier, consider fueling the next update with a small donation.

<br>

<div align="center">

<a href="https://buy.stripe.com/dRm9AU1xQ3Ds22N6VK1VK01">
  <img src="https://img.shields.io/badge/Donate-Support%20Me-blue?style=for-the-badge&logo=stripe" alt="Support me">
</a>

</div>

<br>

Your support means the world. Let's build something great together

<br>

<div align="center">

&copy; 2026 Chai Chaimee NVDA Add-on Released under GNU General Public License

</div>