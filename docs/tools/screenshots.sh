#!/bin/bash -ex

# $1: python script to run
# urxvt, xdotool and import are required to run this script

CLASSNAME=$(head -c 6 /dev/urandom | base64 | tr -cd [:alnum:])
PYTHON=python

urxvt -bg gray90 -b 0 +sb -fn '-misc-fixed-medium-*-*-*-*-140-*-*-*-*-*-*' \
	-fb '-misc-fixed-bold-*-*-*-*-140-*-*-*-*-*-*' \
	-name "$CLASSNAME" -e "$PYTHON" "$1" &
RXVTPID=$!
until RXVTWINDOWID=$(xdotool search --classname "$CLASSNAME"); do
	sleep 0.1
done
export RXVTWINDOWID
image=${1%.py}

c=1
while read -r line; do
	# the echo trick is needed to expand RXVTWINDOWID variable
	echo "sending $line"
	echo $line | xdotool -
	sleep 1.0
	import -window "$RXVTWINDOWID" "${image}$c.png"
	(( c++ ))
done

kill $RXVTPID
