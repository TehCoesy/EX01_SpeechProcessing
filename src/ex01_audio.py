import librosa
import soundfile as sf
import sounddevice as sd
import numpy as np
import queue
import sys
import threading

#A little messy, will update later

#Formatting Information
OUTPUT_DIR = "./output"
FILE_APPEND = "sentences"
FILE_EXT = ".wav"

print("SpeechProcessing_EX01\n")

txt_file = open("paragraph.txt", "r")
txt_content = txt_file.readlines()

#Format the sentences
txt_extracted_content = []

#Remove blank spaces
for sc in txt_content:
    sentences = sc.split('.')
    for s in sentences:
        txt_extracted_content.append(s.strip())

#Remove empty strings
txt_extracted_content = [s for s in txt_extracted_content if s]

print("Extracted {} sentences.".format(len(txt_extracted_content)))

print("Type in prefix for recording file_names: (Leave blank for default)")
print("Default is " + FILE_APPEND + "_#.wav")
new_append = input("Input: ")

if (new_append):
    FILE_APPEND = new_append
 
print("Outputting to " + OUTPUT_DIR + "/" + FILE_APPEND + "_#.wav\n")

print("Program will now record the sentences.\n")

#Controls
EXIT_CMD = "/q"

inputQueue = queue.Queue()

def read_kb_input(inputQueue):
    while True:
        input_str = input()
        inputQueue.put(input_str)

#Recording functions
SAMPLE_RATE = 22050
CHANNELS = 2

q = queue.Queue()

def callback( indata, frames, time, status):
    #This is called (from a separate thread) for each audio block.
    if status:
        print(status, file=sys.stderr)
    q.put(indata.copy())

def record(file_name):

    try:
        #Open a new soundfile and attempt recording
        with sf.SoundFile(file_name, mode='x', samplerate=SAMPLE_RATE, channels=CHANNELS, subtype="PCM_24") as file:
            with sd.InputStream(samplerate=SAMPLE_RATE, device=sd.default.device, channels=CHANNELS, callback=callback):
                print("Recording ... ('/q' to stop recording)")
                

                while True:
                    file.write(q.get())

                    if (inputQueue.qsize() > 0):
                        input_str = inputQueue.get()
                        if (input_str == EXIT_CMD):
                            break
                print("Saved to: {}\n".format(file_name))

    except Exception as e:
        print(e)



#Recording

inputThread = threading.Thread(target=read_kb_input, args=(inputQueue,))
inputThread.start()

i = 0
for s in txt_extracted_content:
    print("\"{}.\"\n".format(s))
    file_name = OUTPUT_DIR + "/" + FILE_APPEND + "_{}.wav".format(i)
    i += 1
    print("Output: " + file_name)
    input("Press any key to start recording.")
    record(file_name)
