from warden.terminal import load_terminals
from warden.memory import LocalPhotoMemory

mem = LocalPhotoMemory("../images")
terminals = load_terminals('../terminals.yaml', mem)
for terminal in terminals:
    print(f"Terminal: {terminal.name}")
    for camera in terminal.cameras:
        print(f"CAMERA FULLNAME {camera.full_name}")
        camera.get()
        camera.save_last()
