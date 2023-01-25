import os
import fnmatch

import soundfile as sf
import numpy as np
import wave

from midi2audio import FluidSynth

def MIDI2WAV(name, output_path, merge=True) :

    print("MXL to WAV")

    fs = FluidSynth()
    
    # save data list
    matches = []
    for root, dirnames, filenames in os.walk(output_path):
            for filename in fnmatch.filter(filenames, '*.mid'):
                matches.append(os.path.join(root, filename))

    num = 0
    #convert midi to audio
    for midi in matches :
        file_name = os.path.splitext(os.path.basename(midi))[0]
        fs.play_midi(output_path + f'/{file_name}.mid')
        fs.midi_to_audio(output_path + f'/{file_name}.mid', output_path + f'/{name}_{num}.wav')
        num += 1

    # # if merge True
    # # merge midi file
    # if merge:
    #     print('merge file...')
    #     outfile = f"{name}.wav"

    #     merge_file = []
    #     for song in matches:
    #         file_name = os.path.splitext(os.path.basename(song))[0]
    #         new_file = output_path + f'{file_name}.wav'

    #     output = wave.open(outfile, 'wb')
    #     output.setparams(merge_file[0][0])
    #     for i in range(len(merge_file)):
    #         output.writeframes(merge_file[i][1])

    #     output.close()

    return