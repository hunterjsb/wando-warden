from warden.terminal import load_terminals
from warden.memory import LocalPhotoMemory
from warden.ocr import extract_timestamp


mem = LocalPhotoMemory("../images")
terminals = load_terminals('../terminals.yaml', mem)
for terminal in terminals:
    print(f"\nTerminal: {terminal.name}")
    for camera in terminal.cameras:
        camera.get()
        camera.save_last(with_timestamp=True)
        print(f"CAMERA: {camera.full_name} @ {camera.last_timestamp}")
