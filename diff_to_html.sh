#!/bin/bash

f1=$1
f2=$2

/usr/bin/vimdiff $f1 $f2 <<EOF
:set number
:TOhtml
:w! $3
:qall!
EOF
