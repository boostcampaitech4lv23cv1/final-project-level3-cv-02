import os
import fnmatch
import pydub

def WAV2MP3(output_path) :
    print("MXL to MP3")
    matches = []
    for root, dirnames, filenames in os.walk(output_path):
            for filename in fnmatch.filter(filenames, '*.wav'):
                matches.append(os.path.join(root, filename))

    for wav in matches :
        file_name = os.path.splitext(os.path.basename(wav))[0]
        sound = pydub.AudioSegment.from_wav(output_path + f"/{file_name}.wav")
        sound.export(output_path + f"/{file_name}.mp3", format="mp3")
    
    return


def WAV2FLAC(output_path) :
    print("MXL to FLAC")
    matches = []
    for root, dirnames, filenames in os.walk(output_path):
            for filename in fnmatch.filter(filenames, '*.wav'):
                matches.append(os.path.join(root, filename))

    for wav in matches :
        file_name = os.path.splitext(os.path.basename(wav))[0]
        sound = pydub.AudioSegment.from_wav(output_path + f"/{file_name}.wav")
        sound.export(output_path + f"/{file_name}.flac", format="flac")
    
    return