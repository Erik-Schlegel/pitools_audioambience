#!/usr/bin/env python3

import argparse
import threading
import sounddevice as sd
import signal
import sys
import time
import numpy as np
from pydub import AudioSegment
import logging
import subprocess
import termios

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        logging.error(message)
        self.print_help()
        sys.exit(2)

# Use the custom argument parser
parser = CustomArgumentParser(description='Play audio files with specified volume adjustment, trimming, offset start, and panning in a loop')
parser.add_argument('-c', '--config', type=str, required=True, help='Path to a configuration file is required.')
args = parser.parse_args()

stop_threads = False

# Apply panning to the audio data
def apply_panning(audio_data, panning, is_mono):
    if panning < -1 or panning > 1:
        logging.error(f"Invalid panning value {panning}. It should be between -1 and 1.")
        return audio_data

    if is_mono:
        if panning == -1:
            audio_data = np.column_stack((audio_data, np.zeros_like(audio_data)))
        elif panning == 1:
            audio_data = np.column_stack((np.zeros_like(audio_data), audio_data))
        else:
            left_gain = (1 - panning) / 2
            right_gain = (1 + panning) / 2
            audio_data = np.column_stack((audio_data * left_gain, audio_data * right_gain))
    else:
        left_gain = (1 - panning) / 2
        right_gain = (1 + panning) / 2
        audio_data[:, 0] *= left_gain
        audio_data[:, 1] *= right_gain

    return audio_data

# Play an audio file with specified volume adjustment, trimming, offset start, and panning in a loop
def play_audio(file, gain_db, trim_start, trim_end, offset_start, panning):
    global stop_threads

    try:
        logging.info(f"Playing file: {file}")
        time.sleep(offset_start / 1000.0)
        audio_segment = AudioSegment.from_file(file)
        logging.debug(f"Loaded audio file: {file}")

        # Trim the specified milliseconds from the start and end of the audio file
        duration = len(audio_segment)
        audio_segment = audio_segment[trim_start:duration - trim_end]
        logging.debug(f"Trimmed audio segment: start={trim_start}, end={duration - trim_end}")

        # Apply gain adjustment
        audio_segment = audio_segment + gain_db
        logging.debug(f"Adjusted volume by {gain_db} dB")

        is_mono = audio_segment.channels == 1
        audio_data = np.array(audio_segment.get_array_of_samples()).reshape((-1, audio_segment.channels)).astype(np.float32) / (1 << 15)
        audio_data = apply_panning(audio_data, panning, is_mono)
        frame_rate = audio_segment.frame_rate
        buffer_size = 4096

        def callback(outdata, frames, time, status):
            if status:
                logging.warning(status)
            start = callback.counter
            end = start + frames
            if end >= len(audio_data):
                outdata[:len(audio_data)-start] = audio_data[start:]
                outdata[len(audio_data)-start:] = audio_data[:frames - (len(audio_data) - start)]
                callback.counter = frames - (len(audio_data) - start)
            else:
                outdata[:] = audio_data[start:end]
                callback.counter += frames

        callback.counter = 0

        with sd.OutputStream(samplerate=frame_rate, channels=2, callback=callback, blocksize=buffer_size) as stream:
            while not stop_threads:
                sd.sleep(1000)
    except Exception as e:
        logging.error(f"Error playing file {file}: {e}")

# Signal handler for graceful exit
def signal_handler(sig, frame):
    global stop_threads
    logging.info("Exiting...")
    stop_threads = True
    restore_terminal_settings()
    sys.exit(0)

# Save the original terminal settings
original_terminal_settings = termios.tcgetattr(sys.stdin)

# Function to restore terminal settings
def restore_terminal_settings():
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, original_terminal_settings)

# Register signal handler
signal.signal(signal.SIGINT, signal_handler)

# Set system volume
def set_system_volume(volume, control='Master'):
    try:
        subprocess.run(['amixer', 'set', control, f'{volume}%'], check=True)
        logging.info(f"System volume set to {volume}% on control {control}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error setting system volume on control {control}: {e}")

# Read the configuration file and start threads for each audio file
def main():
    config_file = args.config
    threads = []

    # Set system volume to 100% (adjust as needed)
    set_system_volume(100)

    try:
        with open(config_file, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):  # Skip empty lines and comments
                    file_path, gain_db, trim_start, trim_end, offset_start, panning = line.split()
                    gain_db = float(gain_db)
                    trim_start = int(trim_start)
                    trim_end = int(trim_end)
                    offset_start = int(offset_start)
                    panning = float(panning)
                    logging.debug(f"Starting thread for file: {file_path}, gain_db: {gain_db}, trim_start: {trim_start}, trim_end: {trim_end}, offset_start: {offset_start}, panning: {panning}")
                    t = threading.Thread(target=play_audio, args=(file_path, gain_db, trim_start, trim_end, offset_start, panning))
                    t.start()
                    threads.append(t)
    except Exception as e:
        logging.error(f"Error reading configuration file: {e}")
        sys.exit(1)

    # Keep the main thread running
    for t in threads:
        t.join()

if __name__ == '__main__':
    main()
