
PYTHON_SOURCE=$(shell echo */*.py.xdotool)
TARGETS=${PYTHON_SOURCE:.py.xdotool=1.png}
TOOLS=tools/compile_pngs.sh tools/screenshots.sh
EXTERNAL_PROGRAMS=Xvfb urxvt xdotool

.PHONY: all clean ${EXTERNAL_PROGRAMS}

all: ${TARGETS}

${TARGETS}: %1.png: %.py %.py.xdotool ${TOOLS} ${EXTERNAL_PROGRAMS}
	tools/compile_pngs.sh $<

${EXTERNAL_PROGRAMS}:
	@if ! which $@ > /dev/null ; then (echo "Need to install $@"; return 1 ); fi

apt-get-dependencies:
	sudo apt-get install xvfb rxvt-unicode xdotool

clean:
	rm -f ${TARGETS}
