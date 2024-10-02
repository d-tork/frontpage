#!/bin/bash

################################################################################
#
# Runner for gutensearch as a docker executable
#
# Must be interactive to answer python prompt.
#
################################################################################
cachedir="$HOME/.cache/gutensearch/"

docker run --rm \
	--interactive --tty \
	--network=frontpage_default \
	--mount type=bind,source="$cachedir",target=/cache \
	gutensearch $@
