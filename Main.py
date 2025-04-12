import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import platform

p = pyaudio.PyAudio()

chunk = 4096
audio_format = pyaudio.paInt16
audio_rate = 48000

def manual_device_selection():
    """
    Allows the user to manually select their audio input device when one can not be identified automatically.
    
    The available input options are limited to those with at least one input channel to decrease unusable options.

    Returns:
        index (int or None): The index of the input device available, or 
                             None if no such device is found.
        num_channels (int or None): The number of input channels associated with the device, 
                                    or None if no such device is found.
    """
    
    print("\nAvailable Input Devices:\n")
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            print(f"{i}: {info['name']} (Input Channels: {info['maxInputChannels']})")

    try:
        selected = int(input("\nEnter the index of the device you want to use: "))
        selected_info = p.get_device_info_by_index(selected)
        return selected, selected_info['maxInputChannels']
    except (ValueError, IOError):
        print("Invalid selection. Exiting.")
        return None, None


def find_input_device():
    """
    Searches through the user's available input devices to locate one suitable for capturing 
    system audio. Specifically, it looks for a device whose name starts with 'Stereo Mix', 
    which is commonly available on Windows systems using Realtek(R) drivers.

    This approach allows compatibility with a variety of hardware by checking for any input 
    device beginning with 'Stereo Mix', regardless of the specific audio driver in use.

    Returns:
        index (int or None): The index of the input device that starts with 'Stereo Mix', or 
                             None if no such device is found.
        num_channels (int or None): The number of input channels associated with the device, 
                                    or None if no such device is found.
    """
    os_name = platform.system()
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        name = info['name'].lower()
        print(f"{i}: {info['name']} (Input Channels: {info['maxInputChannels']})")

        if os_name == "Windows" and name.startswith("stereo mix") and info['maxInputChannels'] > 0:
            print(f"Successfully located Windows audio input through '{info['name']}' (index {i})")
            return i, info['maxInputChannels']
        elif os_name == "Darwin" and "blackhole" in name:
            print(f"Successfully located Mac audio input through '{info['name']}' (index {i})")
            return i, info['maxInputChannels']
    if os_name == "Windows":
        print(
            "\nProper audio recording device not found.\n"
            "Please enable 'Stereo Mix' by going to:\n"
            "Settings → Sound → More Sound Settings → Recording tab\n"
            "then right-click 'Stereo Mix' and select 'Enable'.\n"
            "Also ensure that the 16 bit, 48,000 Hz option is selected."
        )
    elif os_name == "Darwin":
        print(
            "\nNo suitable input found.\n"
            "You may select the device manually or refer to the following and try again:\n"
            "On macOS, please ensure that 'BlackHole' is installed and selected\n"
            "as your system's input device in System Settings → Sound → Input.\n"
            "You may also need to route audio via the Audio MIDI Setup utility."
        )
    else:
        print("Your operating system could not be identified.\n")
    
    print("Would you like to manually select an input device?\n")
    choice = input("Type 'y' to view available options. Type anything else to quit: ").lower()
    if choice == 'y':
        return manual_device_selection()
    else: 
        return None, None

index, num_channels = find_input_device()

if index is None:
    exit()

stream = p.open(format = audio_format,
                channels = num_channels,
                rate = audio_rate,
                input = True,
                input_device_index = index,
                frames_per_buffer = chunk)

fig, ax = plt.subplots()
x = np.arange(0, chunk)
line, = ax.plot(x, np.random.rand(chunk), lw = 2)
ax.set_ylim(-32768, 32767)
ax.set_xlim(0, chunk)
ax.set_title("Live Stereo Mix Waveform")
ax.set_xlabel("Sample")
ax.set_ylabel("Amplitude")

# Update plot with audio
def update(frame):
    """
    Updates the waveform display with the latest chunk of audio data.

    Parameters:
        frame (int): Frame index automatically passed by FuncAnimation (unused here).

    Returns:
        tuple: Updated matplotlib line object for the live plot.
    """
    
    data = stream.read(chunk, exception_on_overflow = False)
    audio_data = np.frombuffer(data, dtype = np.int16)

    if num_channels == 2:
        audio_data = audio_data[::2]

    line.set_ydata(audio_data)
    return line,

animate = animation.FuncAnimation(fig, update, interval=30, blit=True)
plt.show()

stream.stop_stream()
stream.close()
p.terminate()