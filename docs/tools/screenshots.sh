#!/bin/bash

# $1: python script to run
# urxvt, xdotool and import are required to run this script

CLASSNAME=$(head -c 6 /dev/urandom | base64 | tr -cd [:alnum:])
PYTHON=python

urxvt -bg gray90 -b 0 +sb -fn '-misc-fixed-medium-*-*-*-*-140-*-*-*-*-*-*' \
	-fb '-misc-fixed-bold-*-*-*-*-140-*-*-*-*-*-*' \
	-name "$CLASSNAME" -e "$PYTHON" "$1" &
RXVTPID=$!
RXVTWINDOWID=$(xdotool search --sync --classname "$CLASSNAME")
export RXVTWINDOWID
image=${1%.py}

counter=1
while read -r line; do
	# the echo trick is needed to expand RXVTWINDOWID variable
	echo $line | xdotool -
	echo "sending $line"
	import -window "$RXVTWINDOWID" "${image}$counter.png"
	(( counter++ ))
done

kill $RXVTPID
