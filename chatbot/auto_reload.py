"""
Auto-reload service for scanner updates
Automatically detects new scanner files and reloads data
"""

import os
import time
import threading
from datetime import datetime


class AutoReloader:
    def __init__(self, scanner_parser, posts_directory, check_interval=60):
        """
        Initialize auto-reloader.

        Args:
            scanner_parser: ScannerParser instance to reload
            posts_directory: Directory to monitor
            check_interval: Seconds between checks (default 60)
        """
        self.scanner_parser = scanner_parser
        self.posts_directory = posts_directory
        self.check_interval = check_interval
        self.last_check = None
        self.file_count = 0
        self.running = False
        self.thread = None

    def start(self):
        """Start auto-reload monitoring in background thread."""
        if self.running:
            print("Auto-reloader already running")
            return

        self.running = True
        self.file_count = self._count_files()
        self.last_check = datetime.now()

        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()

        print(f"✓ Auto-reloader started (checking every {self.check_interval}s)")

    def stop(self):
        """Stop auto-reload monitoring."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("Auto-reloader stopped")

    def _count_files(self):
        """Count scanner update files in directory."""
        if not os.path.exists(self.posts_directory):
            return 0

        count = 0
        for filename in os.listdir(self.posts_directory):
            if filename.endswith('.md') and 'scanner-update' in filename:
                count += 1
        return count

    def _monitor_loop(self):
        """Background monitoring loop."""
        while self.running:
            try:
                time.sleep(self.check_interval)

                # Check if file count changed
                current_count = self._count_files()

                if current_count != self.file_count:
                    print(f"\n📁 New scanner files detected ({self.file_count} → {current_count})")
                    print("🔄 Reloading data...")

                    # Reload scanner data
                    old_count = len(self.scanner_parser.incidents)
                    self.scanner_parser.load_all_posts()
                    new_count = len(self.scanner_parser.incidents)

                    print(f"✓ Reloaded! Incidents: {old_count} → {new_count}")
                    print(f"   Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

                    self.file_count = current_count
                    self.last_check = datetime.now()

            except Exception as e:
                print(f"Error in auto-reload monitor: {e}")

    def get_status(self):
        """Get current auto-reload status."""
        return {
            'running': self.running,
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'file_count': self.file_count,
            'check_interval': self.check_interval
        }
