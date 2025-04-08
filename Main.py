import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

p = pyaudio.PyAudio()

chunk = 1024
audio_format = pyaudio.paInt16
audio_rate = 48000

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
    
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        name = info['name'].lower()
        print(f"{i}: {info['name']} (Input Channels: {info['maxInputChannels']})")

        if name.startswith("stereo mix") and info['maxInputChannels'] > 0:
            print(f"Successfully located audio input through '{info['name']}' (index {i})")
            return i, info['maxInputChannels']
    
    print(
        "\nProper audio recording device not found.\n"
        "Please enable 'Stereo Mix' by going to:\n"
        "Settings → Sound → More Sound Settings → Recording tab\n"
        "then right-click 'Stereo Mix' and select 'Enable'.\n"
        "Also ensure that the 16 bit, 48,000 Hz option is selected."
    )
    return None, None

index, num_channels = find_input_device()

if index is None:
    exit()

stream = p.open(format=audio_format,
                channels=num_channels,
                rate=audio_rate,
                input=True,
                input_device_index=index,
                frames_per_buffer=chunk)

fig, ax = plt.subplots()
x = np.arange(0, chunk)
line, = ax.plot(x, np.random.rand(chunk), lw=2)
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

# Clean up
stream.stop_stream()
stream.close()
p.terminate()