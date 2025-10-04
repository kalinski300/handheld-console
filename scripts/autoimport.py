import time, os, shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

ROM_ROOT = os.path.join(os.path.dirname(__file__), "..", "roms")
DOWNLOADS = os.path.join(os.path.dirname(__file__), "..", "downloads")

# Supported systems
EXT_TO_SYSTEM = {
    ".nes": "nes",
    ".sfc": "snes",
    ".gba": "gba"
}

class ROMHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        _, ext = os.path.splitext(event.src_path)
        ext = ext.lower()

        if ext in EXT_TO_SYSTEM:
            system = EXT_TO_SYSTEM[ext]
            dest_dir = os.path.join(ROM_ROOT, system)
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, os.path.basename(event.src_path))

            # Move the file
            try:
                shutil.move(event.src_path, dest_path)
                print(f"Moved {event.src_path} → {dest_path}")
            except Exception as e:
                print(f"Failed to move {event.src_path}: {e}")
        else:
            print(f"Ignoring unsupported file: {event.src_path}")

if __name__ == "__main__":
    os.makedirs(DOWNLOADS, exist_ok=True)

    event_handler = ROMHandler()
    observer = Observer()
    observer.schedule(event_handler, DOWNLOADS, recursive=False)
    observer.start()
    print("Watching for new ROMs in downloads/ ...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
