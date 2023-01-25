# install ffmpeg and fluidsynth

# Linux
echo "Installing ffmpeg:"
apt-get install ffmpeg
echo "Installing FluidSynth:"
apt-get install fluidsynth

echo "Preparing folder to run... "
mkdir -p ./data
mkdir -p ./data/.xml
mkdir -p ./data/.fluidsynth
mkdir -p ./data/output

echo "Installing sound fonts:"
wget "https://github.com/musescore/MuseScore/raw/master/share/sound/FluidR3Mono_GM.sf3" -P ./data/.fluidsynth

echo "Install finished!"