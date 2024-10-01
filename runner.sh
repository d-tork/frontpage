#!/usr/bin/bash

################################################################################
#
# Runner for gutensearch as a docker executable
#
# Bind-mounts a dotfolder in user's home
#
################################################################################

cachedir="$HOME/.cache/gutensearch"
mkdir -p "$cachedir"
docker run --rm \
	--mount type=bind,source="$cachedir",target=/cache \
	--network=frontpage_default \
	gutensearch $@
