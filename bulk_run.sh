#!/bin/bash

cachedir="$HOME/.cache/gutensearch/"
for dir in $cachedir/epub/*/; do 
	dir=${dir%*/} 
	id="${dir##*/}"
	./runner.sh "$id" --offline --limit 2 
done
