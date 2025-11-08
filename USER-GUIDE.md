# Quick Snippet Overlay - User Guide

Complete guide to using Quick Snippet Overlay for Windows 11.

**Version**: 1.0.0
**Last Updated**: November 6, 2025

---

## Table of Contents

1. [Installation](#installation)
2. [Getting Started](#getting-started)
3. [Basic Usage](#basic-usage)
4. [Advanced Features](#advanced-features)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)
7. [Tips & Best Practices](#tips--best-practices)

---

## Installation

### System Requirements

- **Operating System**: Windows 11 (Windows 10 may work but not tested)
- **Disk Space**: 100MB (50MB for executable + 50MB for data)
- **Memory**: 50MB RAM typical usage
- **Permissions**: User-level (no admin required)

### Installation Steps

1. **Download the Executable**
   - Locate `QuickSnippetOverlay.exe` in the `dist/` folder
   - File size: ~47MB
   - No installation wizard required

2. **Choose a Location**
   - Recommended: `C:\Program Files\QuickSnippetOverlay\`
   - Or any folder you prefer (e.g., `C:\Apps\`, Desktop, etc.)
   - The executable is portable - no registry modifications

3. **First Run**
   - Double-click `QuickSnippetOverlay.exe`
   - The application will:
     - Create configuration folder: `C:\Users\YourName\.quick-snippet-overlay\`
     - Generate default config: `config.yaml`
     - Create empty snippets file: `snippets.yaml`
     - Start in system tray

4. **Verify Installation**
   - Look for the system tray icon (bottom-right of screen)
   - Right-click icon to see the menu
   - Press `Ctrl+Shift+Space` to test the overlay

---

## Getting Started

### Your First Snippet

Let's create a simple snippet to get familiar with the application:

1. **Open the Overlay**
   - Press `Ctrl+Shift+Space` anywhere in Windows

2. **Add a New Snippet**
   - Click the green `+` button (top-right corner)
   - Or press `Ctrl+N`

3. **Fill in the Form**
   ```
   Name:        Hello World
   Description: A simple greeting
   Tags:        test, greeting
   Content:     Hello! This is my first snippet.
   ```

4. **Save the Snippet**
   - Click the **Save** button
   - The overlay will refresh automatically

5. **Test Your Snippet**
   - Type "hello" in the search box
   - Your snippet should appear
   - Press `Enter` to copy it
   - Open Notepad and paste (`Ctrl+V`)

Congratulations! You've created your first snippet. 🎉

---

## Basic Usage

### Opening the Overlay

There are two ways to open the overlay:

1. **Global Hotkey** (Recommended)
   - Press `Ctrl+Shift+Space` from anywhere
   - Works in any application
   - Overlay appears on the monitor with your mouse cursor

2. **System Tray Menu**
   - Right-click the tray icon
   - Select "Show Overlay"

### Searching for Snippets

#### Empty Search
- When the overlay first opens, you'll see up to 10 snippets (alphabetically)
- This is your "quick access" view

#### Fuzzy Search
- Start typing to filter snippets
- Search matches: name, description, tags, and content
- Typo-tolerant: "pyton" will match "python"
- Case-insensitive: "HELLO" matches "hello"

**Search Examples:**
- `git` → finds all Git-related snippets
- `email` → finds email templates
- `flask` → finds Flask code snippets

#### Navigating Results
- **Arrow keys** (↑↓): Move selection
- **Enter**: Copy selected snippet
- **Esc**: Close overlay without copying

### Adding Snippets

#### Method 1: Quick Add (Recommended)

1. Open overlay (`Ctrl+Shift+Space`)
2. Press `Ctrl+N` or click the `+` button
3. Fill in the form:
   - **Name** (required): Display name
   - **Description** (optional): For better search results
   - **Tags** (optional): Comma-separated keywords
   - **Content** (required): The snippet text
4. Click **Save**

**Tips:**
- Use descriptive names for better search
- Tags are automatically normalized (lowercase, spaces → dashes)
- Content supports multi-line text

#### Method 2: Edit YAML File (Advanced)

1. Right-click system tray icon
2. Select "Edit Snippets"
3. Your default editor opens the YAML file
4. Add snippet manually (see [YAML Format](#yaml-format))
5. Save the file
6. Changes reload automatically (within 500ms)

### Copying Snippets

Once you've selected a snippet:

1. **Press Enter** (or double-click with mouse)
2. The snippet is copied to clipboard
3. A green "Copied!" message appears briefly
4. The overlay closes after 500ms
5. Paste anywhere with `Ctrl+V`

---

## Advanced Features

### Variable Substitution

Create dynamic snippets with placeholders:

#### Basic Variables

```
Hello {{name}}!
```

When you select this snippet, you'll be prompted:
```
Enter value for 'name':
```

#### Variables with Defaults

```
Hello {{name:World}}!
```

The prompt shows the default value (`World`), which you can:
- **Accept**: Just press Enter
- **Override**: Type a different value

#### Multiple Variables

```
Dear {{recipient:Sir/Madam}},

Thank you for your order #{{order_id:12345}}.
Your total is ${{amount:0.00}}.

Best regards,
{{sender:Customer Service}}
```

You'll be prompted for each variable sequentially.

#### Variable Prompt Controls

- **Type value**: Override the default
- **Press Enter**: Accept the default
- **Press Esc**: Cancel and return to overlay (snippet not copied)

### Tag Autocomplete

When adding/editing snippets, the tag input has smart autocomplete:

#### How It Works
1. Start typing a tag: `pyt`
2. Suggestions appear based on existing tags:
   - `python` (exact prefix match)
   - `python-flask` (contains "pyt")
   - `pytest` (typo-tolerant match)
3. Press `Tab` to accept the first suggestion
4. Or click a suggestion from the list

#### Multi-Tag Input
- Separate tags with commas: `python, flask, web`
- Autocomplete works for each tag individually
- Tags are normalized on save (lowercase, spaces → dashes)

**Example:**
```
Input:  Python, Web Dev, Flask API
Saved:  python, web-dev, flask-api
```

### Mass Delete Snippets

Delete multiple snippets at once with filtering:

#### Opening the Delete Dialog

1. Open overlay (`Ctrl+Shift+Space`)
2. Press `Ctrl+D` or click the 🗑️ button
3. The delete dialog opens with all snippets

#### Filtering Snippets

- **Type in filter box**: Filters by name, description, tags, content
- **Checkboxes update**: Only matching snippets remain visible
- **Clear filter**: Delete filter text to see all again

#### Selecting Snippets

- **Individual**: Click checkboxes next to snippets
- **Select All**: Check "Select All" (respects current filter)
- **Deselect All**: Uncheck "Select All"

#### Deleting Snippets

1. Select snippets to delete (checkboxes)
2. Click "Delete Selected" button
3. Confirmation dialog shows:
   - Number of snippets to delete
   - List of snippet names
4. Click "Yes" to confirm deletion
5. Click "No" to cancel

**Warning**: Deletion is permanent! Make backups of your `snippets.yaml` file regularly.

### Draggable Overlay

The overlay window can be repositioned:

- **Click and drag**: Click anywhere on the dark background and drag
- **Position persists**: During the current session only
- **Next launch**: Overlay recenters on active monitor

### Multi-Monitor Support

If you have multiple monitors:

- Overlay appears on the monitor with your mouse cursor
- Hotkey always centers overlay on the "active" monitor
- Works with different monitor resolutions and layouts

---

## Configuration

### Configuration File Location

```
C:\Users\<YourUsername>\.quick-snippet-overlay\config.yaml
```

### Default Configuration

```yaml
snippet_file: "C:/Users/<YourUsername>/.quick-snippet-overlay/snippets.yaml"
hotkey: "ctrl+shift+space"
overlay_width: 600
overlay_height: 400
overlay_opacity: 0.95
theme: "dark"
search_debounce_ms: 150
fuzzy_threshold: 60
max_results: 10
```

### Configuration Options

| Option | Description | Default | Valid Values |
|--------|-------------|---------|--------------|
| `snippet_file` | Path to snippets YAML file | `~/.quick-snippet-overlay/snippets.yaml` | Any valid file path |
| `hotkey` | Global hotkey combination | `ctrl+shift+space` | See [Hotkey Format](#hotkey-format) |
| `overlay_width` | Overlay window width (pixels) | `600` | 400-1200 |
| `overlay_height` | Overlay window height (pixels) | `400` | 300-800 |
| `overlay_opacity` | Window transparency | `0.95` | 0.5-1.0 (0.5=50%, 1.0=100%) |
| `theme` | Color theme | `dark` | `dark` only (light mode planned) |
| `search_debounce_ms` | Search delay (milliseconds) | `150` | 50-500 |
| `fuzzy_threshold` | Minimum search score (0-100) | `60` | 40-90 |
| `max_results` | Maximum results shown | `10` | 5-50 |

### Hotkey Format

Current supported format: `ctrl+shift+space`

**Components:**
- `ctrl` - Ctrl key
- `shift` - Shift key
- `space` - Spacebar

**Note**: Other key combinations require code modification. See `src/hotkey_manager.py` for details.

### Changing Configuration

1. **Close the application** (Right-click tray → Quit)
2. **Edit the config file** in a text editor
3. **Save the file**
4. **Restart the application**

**Example**: Change overlay size to 800x600
```yaml
overlay_width: 800
overlay_height: 600
```

---

## YAML Format

### Snippets File Location

```
C:\Users\<YourUsername>\.quick-snippet-overlay\snippets.yaml
```

### File Structure

```yaml
version: 1
snippets:
  - id: unique-identifier-1
    name: Snippet Name
    description: Brief description for search
    content: |
      Multi-line content goes here
      Second line
      {{variable:default}}
    tags:
      - tag1
      - tag2
    created: 2025-11-06
    modified: 2025-11-06

  - id: unique-identifier-2
    name: Another Snippet
    content: Single line content
    tags: [quick, inline, format]
```

### Field Descriptions

#### Required Fields

- **id**: Unique identifier (generated automatically)
  - Format: lowercase, hyphens, no spaces
  - Example: `git-commit-template-001`

- **name**: Display name (shown in search results)
  - Max length: ~100 characters
  - Example: `Git Commit Template`

- **content**: The snippet text
  - Supports multi-line with `|` syntax
  - Supports variables with `{{variable:default}}`
  - Example:
    ```yaml
    content: |
      Line 1
      Line 2
      {{variable:default}}
    ```

#### Optional Fields

- **description**: Search description
  - Helps with search discoverability
  - Example: `Professional email greeting template`

- **tags**: Keywords for organization
  - List format: `[tag1, tag2]` or multi-line format
  - Automatically normalized (lowercase, spaces → dashes)
  - Example: `[email, professional, template]`

- **created**: Creation date (YYYY-MM-DD)
  - Automatically set when using GUI
  - Example: `2025-11-06`

- **modified**: Last modified date (YYYY-MM-DD)
  - Updated automatically by GUI
  - Example: `2025-11-06`

### Manual Editing Tips

1. **Always use proper YAML syntax**
   - Indentation with 2 spaces (not tabs)
   - Use `|` for multi-line content
   - Quote strings with special characters

2. **Ensure unique IDs**
   - Duplicate IDs are auto-fixed with `-1`, `-2` suffix
   - But better to avoid duplicates

3. **Test after editing**
   - Save the file
   - Check overlay (opens within 500ms)
   - If error: check YAML syntax

4. **Backup before manual edits**
   - Copy `snippets.yaml` to `snippets.yaml.backup`
   - Automatic backups saved in same folder (up to 5)

---

## Troubleshooting

### Application Won't Start

#### Error: "Already Running"

**Cause**: Another instance is running, or stale lock file.

**Solution:**
1. Check system tray for existing icon
2. If no icon, delete lock file:
   ```
   C:\Users\<YourUsername>\.quick-snippet-overlay\app.lock
   ```
3. Restart the application

#### Error: "Failed to start"

**Cause**: Missing configuration or permissions issue.

**Solution:**
1. Delete config folder:
   ```
   C:\Users\<YourUsername>\.quick-snippet-overlay\
   ```
2. Restart - it will recreate defaults

### Overlay Not Appearing

#### Hotkey does nothing

**Causes:**
- Another application using `Ctrl+Shift+Space`
- Hotkey listener crashed

**Solutions:**
1. Try opening from system tray menu
2. Restart the application
3. Check config file hotkey setting
4. Try different hotkey (requires config edit)

#### Overlay appears but is blank

**Causes:**
- No snippets in file
- Snippets file has errors

**Solutions:**
1. Add a test snippet via tray menu
2. Check snippets file syntax
3. Right-click tray → "Reload Snippets"

### Search Not Finding Snippets

#### All searches return empty

**Cause**: Fuzzy threshold too high.

**Solution:**
1. Edit `config.yaml`
2. Lower `fuzzy_threshold` from 60 to 40
3. Restart application

#### Specific searches don't work

**Cause**: Search text too different from snippet content.

**Solution:**
- Use more common keywords
- Add better tags to snippets
- Improve snippet descriptions

### Snippets Not Updating

#### Changes to YAML not reflecting

**Causes:**
- File not saved
- File watcher crashed
- YAML syntax error

**Solutions:**
1. Ensure file is saved (check timestamp)
2. Use "Reload Snippets" from tray menu
3. Check for YAML validation errors
4. Restart application

#### Added snippet via GUI not appearing

**Cause**: File write error or permissions issue.

**Solutions:**
1. Check file permissions on snippets folder
2. Verify disk space available
3. Check console for error messages
4. Restart application

### Performance Issues

#### Overlay opens slowly

**Causes:**
- Many snippets (1000+)
- Slow disk access

**Solutions:**
- Reduce `max_results` in config (try 5)
- Archive old snippets to separate file
- Run from SSD instead of HDD

#### Search is laggy

**Causes:**
- Search debounce too low
- Very large snippet content

**Solutions:**
- Increase `search_debounce_ms` to 300
- Split large snippets into smaller ones
- Reduce total snippet count

### Clipboard Issues

#### Snippet not copied

**Causes:**
- Clipboard locked by another app
- pyperclip error

**Solutions:**
- Close clipboard-heavy applications
- Try copying again
- Restart application

---

## Tips & Best Practices

### Organizing Snippets

#### Use Descriptive Names
- ✅ Good: "Python Flask App Template"
- ❌ Bad: "template1"

#### Add Detailed Descriptions
- Helps with search discoverability
- Include context: "For REST API responses"

#### Tag Strategically
- Use common keywords: `code`, `email`, `template`
- Use programming languages: `python`, `javascript`, `sql`
- Use topics: `flask`, `git`, `docker`

#### Group Related Snippets
- Use consistent tag patterns
- Example: All Git snippets tagged with `git`

### Creating Effective Snippets

#### Keep Snippets Focused
- One snippet = one purpose
- Split complex snippets into multiple smaller ones

#### Use Variables for Flexibility
- Identify parts that change often
- Example: names, dates, order numbers

#### Test Your Variables
- Ensure defaults make sense
- Use descriptive variable names: `{{customer_name}}` not `{{name}}`

#### Add Context in Descriptions
- When to use this snippet
- What it's for
- Any prerequisites

### Workflow Tips

#### Quick Access Snippets
- Leave search empty to see top 10 (alphabetically)
- Name your most-used snippets starting with numbers: `1-email-template`

#### Keyboard-First Usage
- Learn the keyboard shortcuts
- Faster than using mouse
- `Ctrl+Shift+Space` → Type → `Enter` → Done!

#### Regular Maintenance
- Review snippets monthly
- Delete unused ones
- Update outdated content
- Improve tags and descriptions

#### Backup Your Snippets
- Copy `snippets.yaml` to cloud storage
- Version control with Git
- Export periodically

### Advanced Use Cases

#### Code Templates
```yaml
name: Python Flask Route
content: |
  @app.route('/{{endpoint:api/users}}', methods=['{{method:GET}}'])
  def {{function_name:get_users}}():
      {{code:pass}}
```

#### Email Templates
```yaml
name: Professional Email
content: |
  Dear {{recipient:Sir/Madam}},

  {{body:I hope this email finds you well.}}

  Best regards,
  {{sender:Your Name}}
```

#### Command Templates
```yaml
name: Docker Run Command
content: |
  docker run -d \
    --name {{container_name:myapp}} \
    -p {{port:8080}}:8080 \
    {{image:myapp:latest}}
```

---

## Keyboard Shortcuts Reference

| Shortcut | Action | Context |
|----------|--------|---------|
| `Ctrl+Shift+Space` | Show/hide overlay | Global (anywhere) |
| `↑` / `↓` | Navigate results | Overlay open |
| `Enter` | Copy selected snippet | Overlay open |
| `Esc` | Close overlay | Overlay open |
| `Ctrl+N` | Add new snippet | Overlay open |
| `Ctrl+D` | Delete snippets dialog | Overlay open |
| `Tab` | Accept tag suggestion | Snippet editor |

---

## Getting Help

### Before Asking for Help

1. **Check this user guide** (you're reading it!)
2. **Review troubleshooting section**
3. **Check configuration file syntax**
4. **Try restarting the application**
5. **Check system tray for icon**

### Reporting Issues

If you encounter a bug:

1. **Describe the problem**:
   - What you expected to happen
   - What actually happened

2. **Steps to reproduce**:
   - Step-by-step instructions

3. **System info**:
   - Windows version
   - Application version

4. **Error messages**:
   - Screenshots helpful
   - Any console output

---

## Appendix

### File Locations

| File | Location |
|------|----------|
| Executable | `<where you put it>/QuickSnippetOverlay.exe` |
| Config | `C:\Users\<You>\.quick-snippet-overlay\config.yaml` |
| Snippets | `C:\Users\<You>\.quick-snippet-overlay\snippets.yaml` |
| Backups | `C:\Users\<You>\.quick-snippet-overlay\snippets.yaml.backup.*` |
| Lock File | `C:\Users\<You>\.quick-snippet-overlay\app.lock` |

### Version History

- **v1.0.0** (2025-11-06)
  - Initial release
  - Standalone executable
  - All core features implemented

---

**Quick Snippet Overlay User Guide v1.0.0**
Last Updated: November 6, 2025
For technical documentation, see `README.md`
