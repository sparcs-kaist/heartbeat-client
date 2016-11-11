#!/bin/bash

if [ $# -ne 2 ]; then
    echo $0: usage: install.sh name key
    exit 1
fi

ROOT_PATH="$(dirname $(readlink -f $0))/heartbeat"

GIT_URL="https://github.com/sparcs-kaist/heartbeat-client.git"
"/usr/bin/git" "clone" "$GIT_URL" "heartbeat"

ENV_PATH="$ROOT_PATH/env"
"/usr/bin/virtualenv" "-p/usr/bin/python3.5" "$ENV_PATH"

. "$ENV_PATH/bin/activate"
"$ENV_PATH/bin/pip" "install" "-r$ROOT_PATH/requirements.txt"

SETTING_PATH="$ROOT_PATH/settings.py"
echo "NETWORK_REPORT = True" >> "$SETTING_PATH"
echo "SERVER_NAME = $1" >> "$SETTING_PATH"
echo "SERVER_KEY = $2" >> "$SETTING_PATH"
echo "API_ENDPOINT = https://example.com/" >> "$SETTING_PATH"

crontab=/usr/bin/crontab
($crontab -l 2>/dev/null; echo "*/2 * * * * cd $ROOT_PATH && ./run.sh") | $crontab -
