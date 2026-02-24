<p align="center">
  <img src="https://www.nvaccess.org/wp-content/uploads/2015/10/NVDA_logo_standard_transparent.png" alt="NVDA Logo" width="200">
</p>

# CMDReader
### *Command Line Accessibility, Redefined.*

**Author:** chai chaimee  
**URL:** [github.com/chaichaimee/CMDReader](https://github.com/chaichaimee/CMDReader)

---

## Stop Guessing. Start Reading.
Working with the Windows Command Prompt (CMD) or PowerShell can be a chaotic experience for screen reader users. **CMDReader** transforms that chaos into clarity. No more struggling to find where the output started or wondering if a process has finished. CMDReader intelligently monitors your console, alerts you to critical events, and gives you total control over your command history with elegant, simple shortcuts.

### Intelligent Features
* **Real-Time Output Monitoring:** Sit back and relax. CMDReader automatically speaks new information as it appears, skipping the "noise" and jumping straight to the data you need.
* **Smart Noise Filtering:** Say goodbye to cluttered output. Our advanced logic strips away trailing spaces and useless decorative lines, leaving you with clean, professional text.
* **Instant Error Alerts:** Never miss a mistake. CMDReader listens for common error keywords and alerts you with a distinct warning tone the moment something goes wrong.
* **Process Completion Signal:** For those long-running tasks, CMDReader will notify you with a "Command Finished" message and a success chime the second your prompt returns.
* **Clean Shadow History:** Navigate through every line of your session history using a dedicated "Shadow Buffer" that is always up-to-date and clutter-free.

---

## How to Navigate
1.  **Monitoring:** Simply focus any CMD or PowerShell window. CMDReader begins working automatically, watching for new text and process updates.
2.  **Scrolling History:** Use `Ctrl+Alt+Up` or `Down` to move line-by-line through the session output without moving your actual cursor.
3.  **Analyzing Logs:** Need to see everything at once? Press `Ctrl+Alt+L` to open a perfectly formatted text file of your current session for deep review or archiving.

### Quick Reference Summary
| Gesture | Action | Result |
| :--- | :--- | :--- |
| `Ctrl+Alt+Up Arrow` | Previous Line | Reads the previous line in history |
| `Ctrl+Alt+Down Arrow` | Next Line | Reads the next line in history |
| `Ctrl+Alt+L` | View Session Log | Opens the cleaned log in your text editor |
| (Automatic) | Error Detection | Distinct Beep (440Hz) on errors |
| (Automatic) | Job Done | "Command Finished" chime (880Hz) |

---

## Under the Hood
CMDReader is built to be lightweight and fast. It captures your console output and stores a cleaned version in a temporary log file located at:
`%appdata%\nvda\CMDReader.txt`

This ensures you always have a "paper trail" of your work, formatted perfectly without the typical console whitespace clutter.

---

## Support the Developer
If you enjoy using **CMDReader** and find it helpful, feel free to support my work and future development.

**Donate here:** [Support the Project](https://github.com/chaichaimee)

---
© 2026 CMDReader Add-on for NVDA. Version 2026.1