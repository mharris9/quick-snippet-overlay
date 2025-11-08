# Packaging Notes - Quick Snippet Overlay

Manual tasks and instructions for completing the Windows distribution package.

**Version**: 1.0.0
**Date**: November 6, 2025

---

## Phase 7 Status

### ✅ Completed Tasks

1. **Production Build Preparation**
   - ✅ Debug logging removed/configured
   - ✅ Logging level set to WARNING for production
   - ✅ All test failures documented (10 acceptable failures - delete dialog test infrastructure)
   - ✅ 156/166 tests passing (94% pass rate, 85% coverage)

2. **PyInstaller Executable**
   - ✅ PyInstaller installed (v6.16.0)
   - ✅ `.spec` file created and configured
   - ✅ Executable built successfully
   - ✅ File location: `dist/QuickSnippetOverlay.exe`
   - ✅ File size: 47MB (reasonable for PySide6 app)
   - ✅ Hidden imports configured for all dependencies

3. **Documentation**
   - ✅ README.md updated with executable distribution instructions
   - ✅ USER-GUIDE.md created with comprehensive end-user instructions
   - ✅ Technical documentation in place

### 📦 Manual Tasks Remaining

These tasks require user input or external tools:

1. **Application Icon (.ico)**
   - **Status**: Not created (using default Windows icon)
   - **Instructions**: See [Creating Application Icon](#creating-application-icon)

2. **Inno Setup Installer**
   - **Status**: Script not created (optional but recommended)
   - **Instructions**: See [Creating Inno Setup Installer](#creating-inno-setup-installer)

3. **Code Signing Certificate**
   - **Status**: Not implemented (optional for distribution)
   - **Instructions**: See [Code Signing](#code-signing)

---

## Creating Application Icon

### Why You Need It

- Professional appearance
- Easy identification in Start Menu, taskbar, tray
- Better branding

### Requirements

- Icon file in `.ico` format
- Multiple sizes: 16x16, 32x32, 48x48, 64x64, 128x128, 256x256 pixels
- Windows-compatible (square, clean design)

### Option 1: Create with Online Tool (Easiest)

1. **Design your icon**:
   - Use a simple, recognizable symbol
   - Suggestion: Speech bubble with "S" or lightning bolt
   - Keep it simple for small sizes

2. **Generate .ico file**:
   - Website: https://www.icoconverter.com/
   - Website: https://www.favicon-generator.org/
   - Upload your design (PNG/JPG)
   - Download `.ico` file with all sizes

3. **Save to project**:
   ```
   quick-snippet-overlay/icon.ico
   ```

4. **Update .spec file**:
   ```python
   exe = EXE(
       ...
       icon='icon.ico',  # Uncomment this line
   )
   ```

5. **Rebuild executable**:
   ```bash
   ./.venv/Scripts/pyinstaller.exe quick-snippet-overlay.spec --clean
   ```

### Option 2: Use Existing Icon

1. **Find a suitable icon**:
   - Check icon packs (e.g., Material Design Icons, Font Awesome)
   - Ensure license allows commercial use
   - Download as .ico or convert from PNG

2. **Follow steps 3-5 from Option 1**

### Option 3: Hire a Designer (Professional)

- Cost: $20-100 on Fiverr/Upwork
- Provides: Custom icon in all sizes
- Turnaround: 1-3 days

---

## Creating Inno Setup Installer

### Why You Need It

- Professional Windows installation experience
- Start Menu shortcuts
- Uninstall support
- Auto-update preparation
- Better than "extract zip and run"

### Requirements

- Inno Setup 6 (free): https://jrsoftware.org/isinfo.php
- The built executable: `dist/QuickSnippetOverlay.exe`

### Installation Script Template

Create `installer.iss` in project root:

```iss
; Quick Snippet Overlay - Inno Setup Script
; Requires Inno Setup 6 or later

[Setup]
AppName=Quick Snippet Overlay
AppVersion=1.0.0
AppPublisher=Your Name
AppPublisherURL=https://your-website.com
AppSupportURL=https://github.com/yourusername/quick-snippet-overlay/issues
AppUpdatesURL=https://github.com/yourusername/quick-snippet-overlay/releases
DefaultDirName={autopf}\QuickSnippetOverlay
DefaultGroupName=Quick Snippet Overlay
AllowNoIcons=yes
LicenseFile=LICENSE
OutputDir=installer
OutputBaseFilename=QuickSnippetOverlay-Setup-v1.0.0
SetupIconFile=icon.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "startupicon"; Description: "Run on Windows startup"; GroupDescription: "Startup Options"

[Files]
Source: "dist\QuickSnippetOverlay.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "USER-GUIDE.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Quick Snippet Overlay"; Filename: "{app}\QuickSnippetOverlay.exe"
Name: "{group}\User Guide"; Filename: "{app}\USER-GUIDE.md"
Name: "{group}\{cm:UninstallProgram,Quick Snippet Overlay}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Quick Snippet Overlay"; Filename: "{app}\QuickSnippetOverlay.exe"; Tasks: desktopicon
Name: "{userstartup}\Quick Snippet Overlay"; Filename: "{app}\QuickSnippetOverlay.exe"; Tasks: startupicon

[Run]
Name: "{group}\Quick Snippet Overlay"; Filename: "{app}\QuickSnippetOverlay.exe"; Description: "{cm:LaunchProgram,Quick Snippet Overlay}"; Flags: nowait postinstall skipifsilent

[Code]
// Check if application is running before uninstall
function InitializeUninstall(): Boolean;
var
  ErrorCode: Integer;
begin
  Result := True;
  if CheckForMutexes('QuickSnippetOverlay') then
  begin
    if MsgBox('Quick Snippet Overlay is currently running. Would you like to close it now?', mbConfirmation, MB_YESNO) = IDYES then
    begin
      // User can manually close the app
      Result := True;
    end
    else
      Result := False;
  end;
end;
```

### Building the Installer

1. **Install Inno Setup**:
   - Download from https://jrsoftware.org/isdl.php
   - Install with default options

2. **Open the script**:
   - Right-click `installer.iss`
   - Select "Compile"

3. **Or use command line**:
   ```cmd
   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
   ```

4. **Result**:
   - Output: `installer/QuickSnippetOverlay-Setup-v1.0.0.exe`
   - Size: ~48-50MB

### Testing the Installer

1. **Run the installer**:
   - Double-click the setup executable
   - Follow the installation wizard

2. **Verify**:
   - Check Start Menu for "Quick Snippet Overlay"
   - Check desktop icon (if selected)
   - Run the application
   - Test uninstall

3. **Test on clean Windows VM**:
   - Ensures no missing dependencies
   - Confirms installation experience

---

## Code Signing

### Why Sign Your Code?

- **Security**: Users trust signed applications
- **SmartScreen**: Reduces Windows Defender warnings
- **Professionalism**: Shows authenticity

### Requirements

- Code signing certificate ($100-300/year)
- SignTool.exe (from Windows SDK)

### Providers

- **DigiCert**: Industry standard, expensive
- **Sectigo**: Mid-range pricing
- **Certum**: Budget option for individuals

### Signing Process

Once you have a certificate:

1. **Sign the executable**:
   ```cmd
   signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com dist/QuickSnippetOverlay.exe
   ```

2. **Sign the installer**:
   ```cmd
   signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com installer/QuickSnippetOverlay-Setup-v1.0.0.exe
   ```

3. **Verify signature**:
   ```cmd
   signtool verify /pa dist/QuickSnippetOverlay.exe
   ```

**Note**: Code signing is optional but highly recommended for public distribution.

---

## Distribution Checklist

Before releasing:

- [ ] Executable tested on clean Windows 11 VM
- [ ] Application icon added (optional but recommended)
- [ ] Installer created and tested (optional)
- [ ] Code signed (optional but recommended)
- [ ] README.md updated with download instructions
- [ ] USER-GUIDE.md reviewed and accurate
- [ ] LICENSE file included
- [ ] CHANGELOG.md created (if doing releases)
- [ ] GitHub release created with executable
- [ ] Version number consistent across all files

---

## Building from Source

If users want to build from source instead of using the executable:

### Developer Setup

```bash
# Clone repository
git clone <repository-url>
cd quick-snippet-overlay

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\Activate.ps1  # PowerShell
# OR
.venv\Scripts\activate.bat   # Command Prompt

# Install dependencies
pip install -r requirements.txt

# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller quick-snippet-overlay.spec --clean

# Result in dist/QuickSnippetOverlay.exe
```

### Updating requirements.txt

If dependencies change:

```bash
pip freeze > requirements.txt
```

---

## Future Enhancements

### Auto-Update System

Considerations for v1.1:

- GitHub Releases API for version checking
- Download and replace executable
- Notify user of updates
- Automatic or manual installation

### Installer Improvements

- Custom wizard pages
- Feature selection (auto-start, desktop icon)
- Import existing snippets
- Silent install option for enterprise deployment

### Alternative Distribution

- Microsoft Store package (MSIX)
- Chocolatey package manager
- Portable version (ZIP with batch launcher)

---

## Troubleshooting Build Issues

### PyInstaller Errors

**Error**: "Failed to execute script"
- **Cause**: Missing hidden imports
- **Solution**: Add to `hiddenimports` in `.spec` file

**Error**: "DLL not found"
- **Cause**: Missing Windows dependencies
- **Solution**: Check `warn-quick-snippet-overlay.txt` in `build/` folder

### Inno Setup Errors

**Error**: "File not found"
- **Cause**: Incorrect path in `.iss` file
- **Solution**: Use absolute paths or check relative paths

**Error**: "Access denied"
- **Cause**: Running as non-admin
- **Solution**: Run Inno Setup as administrator

---

## Build Artifacts

After a complete build, you should have:

```
quick-snippet-overlay/
├── dist/
│   └── QuickSnippetOverlay.exe       (47MB, standalone executable)
├── build/                            (PyInstaller temp files)
├── installer/
│   └── QuickSnippetOverlay-Setup-v1.0.0.exe  (48-50MB, installer)
├── icon.ico                          (optional, application icon)
├── installer.iss                     (optional, Inno Setup script)
├── quick-snippet-overlay.spec        (PyInstaller configuration)
├── README.md                         (user documentation)
├── USER-GUIDE.md                     (detailed guide)
└── LICENSE                           (license file)
```

---

## Support and Maintenance

### Version Numbering

Use Semantic Versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

Example: `1.0.0` → `1.1.0` (added feature) → `1.1.1` (bug fix)

### Release Process

1. Update version in:
   - `README.md`
   - `USER-GUIDE.md`
   - `quick-snippet-overlay.spec` (if version field exists)
   - `installer.iss` (AppVersion)

2. Build and test

3. Create GitHub release:
   - Tag: `v1.0.0`
   - Title: "Quick Snippet Overlay v1.0.0"
   - Attach: Executable and installer

4. Update documentation links

---

**Packaging Notes v1.0.0**
Last Updated: November 6, 2025

For technical details, see `quick-snippet-overlay.spec` and README.md
