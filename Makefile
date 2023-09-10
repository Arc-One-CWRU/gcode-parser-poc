SHELL := /bin/bash

CURA_CONFIG_DIR := ${HOME}/.config/cura/5.3
CURA_SCRIPTS_DIR := ${CURA_CONFIG_DIR}/scripts
CURA_LOG_DIR := ${HOME}/.local/share/cura/5.3/
GCODE_REPO_DIR := ${HOME}/Coding/arc_one/gcode-parser-poc/src

prepare_linux:
	sudo rm -r ${CURA_SCRIPTS_DIR} && mkdir ${CURA_SCRIPTS_DIR}
	sudo cp -r $(shell pwd)/plugins/*.py ${CURA_SCRIPTS_DIR}/ | echo $(shell ls ${CURA_SCRIPTS_DIR})

run_cura_linux:
	GCODE_REPO_DIR=${GCODE_REPO_DIR} ${HOME}/Desktop/UltiMaker-Cura-5.3.1-linux-modern.AppImage

debug_linux:
	cat ${CURA_LOG_DIR}/cura.log | grep -e arcgcode_debug | tail
