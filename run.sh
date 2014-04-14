#!/bin/bash

ROOT="$(pwd)"
TOOL_PATH="$ROOT"
ENV="$ROOT/env"
export LIB="$ROOT/lib"
export DATA="$ROOT/data"

function echoerr {
    echo "$@" 1>&2
}

if [[ -z "$ENV" || ! -d "$ENV" ]]; then
    echoerr "You need to run ./setup_environment.sh ."
    exit 1
fi

if [ -z "$1" ]; then
    echoerr "Usage: $0 tool [arg0] [arg1] [...]"
    exit 1
fi

export PYTHONPATH="$ROOT:$PYTHONPATH"
export LD_LIBRARY_PATH="$LIB:$LD_LIBRARY_PATH"
export DYLD_LIBRARY_PATH="$LIB:$DYLD_LIBRARY_PATH" # for osx

TOOL_NAME="$1";
TOOL_PARAMS="${@:2}"

TOOL=""
for D in ${TOOL_PATH//:/ }; do
    if [ -f "$D/$TOOL_NAME" ]; then
        TOOL="$D/$TOOL_NAME"
        break
    fi
done

source activate "$ENV"

if [ ! -z "$TOOL" ]; then
    # http://tldp.org/LDP/abs/html/comparison-ops.html
    if [[ $TOOL == *.py ]]; then
        TOOL="python $TOOL"
    fi
else
    alias which=which
    SYSTEM_TOOL="$(which $TOOL_NAME)"

    if [ -z "$SYSTEM_TOOL" ]; then
        echoerr "Could not find '$TOOL_NAME'."
        exit 1
    else
        TOOL="$SYSTEM_TOOL"
    fi
fi

echoerr "Running: '$TOOL'"
echoerr "Params : $TOOL_PARAMS"
echoerr "-----------------------"

$TOOL $TOOL_PARAMS < /dev/stdin
