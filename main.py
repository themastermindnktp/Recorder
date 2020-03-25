import sys
import wave
import nltk
import pyaudio

DATA_FOLDER = 'data'
TEXT_FOLDER = 'text'
VOICE_FOLDER = 'voice'

FORMAT = pyaudio.paInt16
FPB = 1024
CHANNELS = 2
RATE = 44100

recorder = pyaudio.PyAudio()
streamer = recorder.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    frames_per_buffer=FPB,
    input=True
)


def record_sentence(name, sentence):
    print(sentence)

    print('Recording...')
    record = []
    keypressed = 0
    while True:
        keypressed = input("Press Enter to stop!")
        data = streamer.read(FPB)
        record.append(data)
        print(',')
        if not keypressed:
            break

    output_file = wave.open(f"{DATA_FOLDER}/{VOICE_FOLDER}/{name}.wav", "wb")
    output_file.setnchannels(CHANNELS)
    output_file.setsampwidth(recorder.get_sample_size(FORMAT))
    output_file.setframerate(RATE)
    output_file.writeframes(b''.join(record))
    output_file.close()



def record_file(name):
    print('Recording ', name,': ')
    input_file = open(f"{DATA_FOLDER}/{TEXT_FOLDER}/{name}.txt", "r")
    text = input_file.read()

    nltk.download('punkt')
    nltk.data.load('nltk:tokenizers/punkt/english.pickle')
    sentences = nltk.sent_tokenize(text)

    index = 0
    for sentence in sentences:
        index += 1
        record_sentence(name + f"_{index}", sentence)

    print('Done!!!')


if __name__ == "__main__":
    name = sys.argv[1]
    record_file(name)
