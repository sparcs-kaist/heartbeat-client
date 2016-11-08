#!/bin/bash

ROOT_PATH="$(dirname $(readlink -f $0))/heartbeat"

GIT_URL="https://github.com/sparcs-kaist/heartbeat-client.git"
"/usr/bin/git" "clone" "$GIT_URL" "heartbeat"

ENV_PATH="$ROOT_PATH/env"
"/usr/bin/virtualenv" "-p/usr/bin/python3.5" "$ENV_PATH"

. "$ENV_PATH/bin/activate"
"$ENV_PATH/bin/pip" "install" "-r$ROOT_PATH/requirements.txt"

crontab=/usr/bin/crontab
($crontab -l 2>/dev/null; echo "* * * * * . $ROOT_PATH/run.sh") | $crontab -
