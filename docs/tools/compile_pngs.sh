#!/bin/bash -e

# args: scripts to capture

DISPLAYNUM=5
SCREENSHOTS=`dirname $0`/screenshots.sh

# TODO: move this to a function which can be easily excluded and documented
XVFB=$(which Xvfb)
if [ -n $XVFB ]; then
	Xvfb :$DISPLAYNUM -screen 0 1024x768x24 &
	XVFBPID=$!

	# export DISPLAY=:$DISPLAYNUM
	# Uncomment this if you want hide the spawned urxvt windows and only want to
	# see the results in the pngs.
	# It will display many warning messages in xdotool. In particular, the messages are:
	#    XGetInputFocus returned the focused window of 1. This is likely a bug in the X server.
	# but it works.

	trap "kill $XVFBPID" EXIT
fi

for script in $@; do
	echo "doing $script"
	if [ -f "${script}.xdotool" ]; then
		"$SCREENSHOTS" "$script" < "${script}.xdotool"
	fi
done
