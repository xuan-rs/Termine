import env

class Keyview:
    def __init__(self) -> None:
        pass

    def char(self):
        def _win():
            import keyboard
            return keyboard.read_key()

        def _linux():
            import evdev
            from evdev import ecodes, KeyEvent
            
            # Automatically scan for the actual keyboard device
            target_device = None
            for path in evdev.list_devices():
                dev = evdev.InputDevice(path)
                if "keyboard" in dev.name.lower() or "kbd" in dev.name.lower():
                    target_device = dev
                    break
            
            if not target_device:
                raise RuntimeError("Keyboard device not found!")

            # Grab the device to intercept key events and prevent terminal leakage
            target_device.grab()
            
            try:
                # Block and wait for key press
                for event in target_device.read_loop():
                    if event.type == ecodes.EV_KEY:
                        key_event = KeyEvent(event)
                        if key_event.keystate == KeyEvent.key_down:
                            return key_event.keycode
            finally:
                # Always release the device, even on KeyboardInterrupt
                target_device.ungrab()

        match env.SysInfo().system:
            case "windows": return _win()
            case "linux":   return _linux()
