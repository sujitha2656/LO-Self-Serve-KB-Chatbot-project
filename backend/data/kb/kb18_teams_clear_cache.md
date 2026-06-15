# Clearing Microsoft Teams Local Cache

## Problem
Teams displays glitches, fails to update online presence, or gets stuck in login loops and needs a cache reset.

## Resolution
1. Close Microsoft Teams completely (right-click the Teams icon in your tray and click Quit).
2. **On Windows**:
   - Press **Windows Key + R** to open the Run window.
   - Enter `%appdata%\Microsoft\Teams` and click OK.
   - Delete all files and folders in this directory.
3. **On macOS**:
   - Open Finder, press Command + Shift + G, and paste: `~/Library/Application Support/Microsoft/Teams`.
   - Move all files inside the directory to Trash.
4. Open Teams and sign back in.

## References
- AV issues: [kb17_teams_av_troubleshooting.md](kb17_teams_av_troubleshooting.md)
- Collaboration support: `collaboration-help@company.com`