#!/usr/bin/bash

################################################################################
#
# Runner for gutensearch as a docker executable
#
# Must be interactive to answer python prompt.
#
################################################################################

cachedir="$HOME/.cache/gutensearch"
mkdir -p "$cachedir"
docker run --rm \
	--interactive --tty \
	--network=frontpage_default \
	gutensearch $@
