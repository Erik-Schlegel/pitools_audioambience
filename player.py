#!/usr/bin/env python3

import argparse
import threading
import sounddevice as sd
import signal
import sys
import time
import numpy as np

from pydub import AudioSegment


class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write("\n")
        sys.stderr.write(f"Error: {message}\n")
        self.print_help()
        sys.stderr.write("\n")
        sys.exit(2)

# Use the custom argument parser
parser = CustomArgumentParser(description='Play audio files with specified volume adjustment, trimming, and offset start in a loop')
parser.add_argument('-c', '--config', type=str, required=True, help='Path to an configuration file is required.')
args = parser.parse_args()


stop_threads = False


# Play an audio file with specified volume adjustment, trimming, and offset start in a loop
def play_audio(file, gain_db, trim_start, trim_end, offset_start):
    global stop_threads

    time.sleep(offset_start / 1000.0)
    song = AudioSegment.from_file(file)

    # Trim the specified milliseconds from the start and end of the audio file
    duration = len(song)
    song = song[trim_start:duration - trim_end]

    song = song + gain_db
    audio_data = np.array(song.get_array_of_samples()).reshape((-1, song.channels)).astype(np.float32) / (1 << 15)
    frame_rate = song.frame_rate
    buffer_size = 1024

    def callback(outdata, frames, time, status):
        if status:
            print(status)
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

    with sd.OutputStream(samplerate=frame_rate, channels=song.channels, callback=callback, blocksize=buffer_size):
        while not stop_threads:
            sd.sleep(1000)


# Signal handler for graceful exit
def signal_handler(sig, frame):
    global stop_threads
    print("\r\nExiting...")
    stop_threads = True
    sys.exit(0)

# Register signal handler
signal.signal(signal.SIGINT, signal_handler)


# Read the configuration file and start threads for each audio file
def main():
    config_file = args.config
    threads = []

    with open(config_file, 'r') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('#'):  # Skip empty lines and comments
                file_path, gain_db, trim_start, trim_end, offset_start = line.split()
                gain_db = float(gain_db)
                trim_start = int(trim_start)
                trim_end = int(trim_end)
                offset_start = int(offset_start)
                t = threading.Thread(target=play_audio, args=(file_path, gain_db, trim_start, trim_end, offset_start))
                t.start()
                threads.append(t)

    # Keep the main thread running
    for t in threads:
        t.join()

if __name__ == '__main__':
    main()
