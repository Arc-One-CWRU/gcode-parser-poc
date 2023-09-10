# ln -sf $(pwd)/*/ $HOME/.config/cura/5.3/scripts &&
# cp -r $HOME/.config/cura/5.3/scripts/plugins/*.py $HOME/.config/cura/5.3/scripts
cp -r $(pwd)/plugins/*.py $HOME/.config/cura/5.3/scripts

PYTHONPATH=$(which python3) $HOME/Desktop/UltiMaker-Cura-5.3.1-linux-modern.AppImage
