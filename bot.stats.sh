botnick="Emijrpbot"

echo "SELECT rev_comment FROM revision WHERE rev_user_text='$botnick';" > bot.stats.query
#sql wikidata < bot.stats.query > bot.stats.sql

edits=$(wc -l bot.stats.sql | cut -d" " -f1)
echo "edits=$edits" | tee bot.stats.txt

labels=$(grep "BOT - Adding labels" bot.stats.sql | grep -ioE "[0-9]+ languages" | cut -d" " -f1 | awk "{ sum += \$1 } END { print sum }")
echo "labels=$labels" | tee -a bot.stats.txt

descriptions=$(grep "BOT - Adding descriptions" bot.stats.sql | grep -ioE "[0-9]+ languages" | cut -d" " -f1 | awk "{ sum += \$1 } END { print sum }")
echo "descriptions=$descriptions" | tee -a bot.stats.txt

aliases=$(grep "BOT - Adding aliases" bot.stats.sql | grep -ioE "[0-9]+ languages" | cut -d" " -f1 | awk "{ sum += \$1 } END { print sum }")
echo "aliases=$aliases" | tee -a bot.stats.txt

python3 bot.stats.py
