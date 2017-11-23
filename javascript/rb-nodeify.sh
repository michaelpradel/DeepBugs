#!/bin/bash

# Convert js files to something compatible with node 4.*

rm -rf .*.js

for file in *.js; do
	echo "Converting file ${file}..."
	new_file=".${file}"
	# Need to use strict for let bindings inside for loop etc.
	sed "0,/\(^[^/]\+\)/ s/\(^[^/]\+\)/\"use strict\";\n\n\1/" $file > $new_file
	# const {spawn} = req... is not allowed
	sed -i "s/const {spawn} = require('child_process')/const spawn = require('child_process').spawn/" "$new_file"
	# Replace all local requires
	sed -i "s/require(\".\//require(\".\/./" $new_file
	# Spread operator not allowed
	sed -i "s/\.\.\.\(.*\));/Object.assign({}, \1));/" $new_file

done
