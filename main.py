import os
import threading

import tkinter
import nltk
import pyaudio
import wave

DATA_DIR = "data"
TEXT_DIR = "texts"
RECORD_DIR = "records"
LOG_DIR = "logs"

TITLE = "Recorder"
RESOLUTION = "600x400"
BUTTON_CONFIG = {
    'height': 1,
    'width': 15
}
LABEL_CONFIG = {
    'wraplength': 500
}

FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
FRAME_PER_BUFFER = 1024


class Recorder:
    def __init__(self):
        self.topic_selection = tkinter.StringVar(root)
        self.topic_selection.set(topics[0])

        self.menu = tkinter.OptionMenu(
            root,
            self.topic_selection,
            *topics
        )
        self.menu.pack()

        self.topic_button = tkinter.Button(
            root,
            text="Select Topic",
            command=self.select_topic,
            **BUTTON_CONFIG
        )
        self.topic_button.pack()
        self.topic_lock = False

        self.sentence = tkinter.Label(
            root,
            text="SELECT A TOPIC!",
            **LABEL_CONFIG
        )
        self.sentence.pack()

        self.start_button = tkinter.Button(
            root,
            text="Start Recording",
            command=self.start_recording,
            **BUTTON_CONFIG
        )
        self.start_button.pack()
        self.start_lock = True

        self.stop_button = tkinter.Button(
            root,
            text="Stop Recording",
            command=self.stop_recording,
            **BUTTON_CONFIG
        )
        self.stop_button.pack()
        self.stop_lock = True

        self.status = tkinter.Label(
            root,
            text="No topic"
        )
        self.status.pack()

        self.next_button = tkinter.Button(
            root,
            text="Next Sentence",
            command=self.next_sentence,
            **BUTTON_CONFIG
        )
        self.next_button.pack()
        self.next_lock = True

        self.is_recording = False

    def select_topic(self):
        if self.topic_lock:
            return

        self.topic = self.topic_selection.get()
        text = open(f"{DATA_DIR}/{TEXT_DIR}/{self.topic}.txt", "r").read()

        nltk.download('punkt')
        nltk.data.load('nltk:tokenizers/punkt/english.pickle')

        self.sentences = nltk.sent_tokenize(text)

        self.current = 0

        self.sentence.config(text=self.sentences[0])
        self.status.config(text="Ready to record")

        try:
            os.mkdir(f"{DATA_DIR}/{RECORD_DIR}/{self.topic}")
        except FileExistsError:
            pass

        self.start_lock = False
        self.next_lock = True

    def start_recording(self):
        if self.start_lock:
            return

        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            frames_per_buffer=FRAME_PER_BUFFER,
            input=True
        )

        self.frames = []

        self.is_recording = True
        self.status.config(text="Recording")

        self.topic_lock = True
        self.start_lock = True
        self.stop_lock = False
        self.next_lock = True

        thread = threading.Thread(target=self.record)
        thread.start()

    def stop_recording(self):
        if self.stop_lock:
            return

        self.is_recording = False

        wave_file = wave.open(
            f"{DATA_DIR}/{RECORD_DIR}/{self.topic}/" +
            f"{self.topic}_{self.current + 1}.wav",
            "wb",
        )

        wave_file.setnchannels(CHANNELS)
        wave_file.setsampwidth(self.audio.get_sample_size(FORMAT))
        wave_file.setframerate(RATE)

        wave_file.writeframes(b''.join(self.frames))
        wave_file.close()

        self.status.config(text="Recorded")

        self.topic_lock = False
        self.start_lock = False
        self.stop_lock = True
        self.next_lock = False

    def next_sentence(self):
        if self.next_lock:
            return

        self.current += 1

        if self.current == len(self.sentences):
            self.next_lock = True
            self.start_lock = True

            self.sentence.config(text="FINISHED!")

            log_file = open(
                f"{DATA_DIR}/{LOG_DIR}/{self.topic}.log",
                "w+"
            )

            for i in range(len(self.sentences)):
                log_file.write(f"{self.sentences[i]}\n")
                log_file.write(f"{self.topic}_{i+1}.wav\n")

            return

        self.sentence.config(text=self.sentences[self.current])
        self.status.config(text="Ready to Record")

        self.next_lock = True

    def record(self):
        while (self.is_recording):
            data = self.stream.read(FRAME_PER_BUFFER)
            self.frames.append(data)


topics = [file[:-4] for file in os.listdir(f"{DATA_DIR}/{TEXT_DIR}")]
topics.sort()

root = tkinter.Tk()
root.title(TITLE)
root.geometry(RESOLUTION)
app = Recorder()
root.mainloop()
