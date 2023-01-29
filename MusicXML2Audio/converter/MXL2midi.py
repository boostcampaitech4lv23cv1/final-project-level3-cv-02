import music21
import os
import fnmatch

def MXL2MIDI(data_path, output_path) :

    print("MXL to MIDI")

    # save data list
    matches = []
    for root, dirnames, filenames in os.walk(data_path):
        for filename in filenames :
            tmp = filename.replace(".musicxml",".xml")
            os.rename(f"{root}/{filename}", f"{root}/{tmp}")

    for root, dirnames, filenames in os.walk(data_path):
        for filename in fnmatch.filter(filenames, '*.xml'):
            matches.append(os.path.join(root, filename))

    # convert musicxml to midi
    for xml in matches:
        file_name = os.path.splitext(os.path.basename(xml))[0]
        c = music21.converter.parse(data_path + f'/{file_name}.xml')
        c.write('mid', output_path + f'/{file_name}.mid')
    
    return