import wave, math, contextlib
import speech_recognition as sr
from moviepy.editor import AudioFileClip
import os
import sys

os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"
dirName = './videos/'


def getListOfFiles(dirName):

    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
                
    return allFiles

listOfFiles = getListOfFiles(dirName)
transcribed_audio_file_name = "transcribed_speech.wav"

for video in listOfFiles:
    audioclip = AudioFileClip(video)
    audioclip.write_audiofile(transcribed_audio_file_name)

    with contextlib.closing(wave.open(transcribed_audio_file_name,'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)

    total_duration = math.ceil(duration / 60)
    print(total_duration,duration)

    pathname = 'video-captions/' + video.split('/')[2].split('.')[0] + '.txt'
    f = open(pathname, "a")
    r = sr.Recognizer()
    for i in range(total_duration):
        with sr.AudioFile(transcribed_audio_file_name) as source:
            audio = r.record(source, offset=i*60, duration=60)
        f = open(pathname, "a")
        f.write(str(i)+": \n")
        try :
            text = r.recognize_google(audio, language = 'en-US')
            f.write(text)
        except sr.UnknownValueError:
            f.write(" ")
        except sr.RequestError:
            f.write(" ")
        f.write("\n")
        del audio
    f.close()


