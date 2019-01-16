#!/bin/bash

cd /data/project/emijrpbot/bot-stats/
source bin/activate
python /data/project/emijrpbot/bot-stats/bot.stats.dump.py $1
deactivate
