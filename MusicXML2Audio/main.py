import sys 
sys.path.append("../MusicXML2Audio")

import os
from constant import MODULE_PATH
from converter.MXL2midi import MXL2MIDI
from converter.midi2wav import MIDI2WAV
from converter.wav2sound import WAV2MP3, WAV2FLAC

#handle

NAME = 'file'
XML_PATH = os.path.join(MODULE_PATH, 'data/.xml')
OUTPUT_PATH = os.path.join(MODULE_PATH, "data/output")

MERGE = True
MP3 = True
FLAC = False

def main(NAME, XML_PATH, OUTPUT_PATH, MERGE, MP3, FLAC) :
    
    MXL2MIDI(XML_PATH, OUTPUT_PATH)
    MIDI2WAV(NAME, OUTPUT_PATH, merge=MERGE)
    if MP3 :
        WAV2MP3(OUTPUT_PATH)
    if FLAC :
        WAV2FLAC(OUTPUT_PATH)
    return

if __name__ == "__main__" :
    main(NAME, XML_PATH, OUTPUT_PATH, MERGE, MP3, FLAC)