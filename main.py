from warden.terminal import load_terminals


_terminals = load_terminals('terminals.yaml')
for terminal in _terminals:
    print(f"Terminal: {terminal.name}")
    for camera in terminal.cameras:
        print(f"  Camera: {camera.name}, URL: {camera.url}")