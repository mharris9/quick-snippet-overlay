"""Quick script to check existing tags in snippets."""
from src.config_manager import ConfigManager
from src.snippet_manager import SnippetManager

cm = ConfigManager()
sm = SnippetManager(cm.get('snippet_file'))
sm.load()
tags = sm.get_all_tags()

print(f"Found {len(tags)} unique tags:")
for tag in tags:
    print(f"  - {tag}")

if len(tags) == 0:
    print("\n⚠️ No tags found! Autocomplete needs existing tags to suggest.")
    print("Add some tags to your snippets first, then autocomplete will work.")
