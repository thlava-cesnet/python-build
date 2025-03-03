#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CESNET.
#
# free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

set -e

#cd tests
#pytest -v -x

cd dist

echo -ne "   test: rclone_pygui --help\r"
read -r -d '' GOLDEN <<- EOT || /bin/true
usage: rclone_pygui [-h] [-d] [-c RCLONE_CONFIG] [-r RCLONE_COMMAND] [-p]

CESNET S3 rclone pygui

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           enable debug outputs (default False)
  -c RCLONE_CONFIG, --rclone_config RCLONE_CONFIG
                        rclone config file (default: ./rclone.conf)
  -r RCLONE_COMMAND, --rclone_command RCLONE_COMMAND
                        rclone command, could be full path to command (default: rclone)
  -p, --password_command
                        run as rclone password command, for internal use
EOT
#echo ">$GOLDEN<"
OUT="$(./rclone_pygui --help)"
#echo ">$OUT<"
diff <(echo "$GOLDEN"| tr -d '\n\t ') <(echo "$OUT" | tr -d '\n\t ')
echo "OK"

echo -ne "   test: rclone_pygui --password_command 0\r"
GOLDEN="abc"
OUT="$(PYGUI_RCLONE_OLDPW=abc PYGUI_RCLONE_NEWPW=def RCLONE_PASSWORD_CHANGE=0 ./rclone_pygui --password_command)"
diff <(echo "$GOLDEN") <(echo "$OUT")
echo "OK"

echo -ne "   test: rclone_pygui --password_command 1\r"
GOLDEN="def"
OUT="$(PYGUI_RCLONE_OLDPW=abc PYGUI_RCLONE_NEWPW=def RCLONE_PASSWORD_CHANGE=1 ./rclone_pygui --password_command)"
diff <(echo "$GOLDEN") <(echo "$OUT")
echo "OK"
