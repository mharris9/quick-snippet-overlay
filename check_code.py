"""Diagnostic script to check what code is actually being loaded"""
import src.overlay_window
import inspect

print("=== Checking show_overlay method ===")
print(inspect.getsource(src.overlay_window.OverlayWindow.show_overlay))
print("\n=== Checking _update_results method ===")
print(inspect.getsource(src.overlay_window.OverlayWindow._update_results))
