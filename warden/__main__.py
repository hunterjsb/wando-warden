from warden.terminal import load_terminals
from warden.memory import LocalPhotoMemory
from warden.ocr import extract_timestamp


mem = LocalPhotoMemory("../images")
terminals = load_terminals('../terminals.yaml', mem)
for terminal in terminals:
    print(f"Terminal: {terminal.name}")
    for camera in terminal.cameras:
        camera.get()
        print(f"CAMERA {camera.full_name}; ts {extract_timestamp(camera.timestamp_box)}\n")
