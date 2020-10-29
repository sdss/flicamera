#!/bin/bash

# The name of the host will be in the form sdss-gfaX or sdss-fvc.
# We want the actor name to be gfaX or fvc
ACTOR=`cut -d'-' -f2 <<< $HOST`
# ACTOR=${ACTOR/gfa/flicamera}

flicamera actor --host 0.0.0.0 --actor-name $ACTOR start --debug
