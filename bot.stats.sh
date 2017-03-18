#Cron example: 0 12    * * *   /usr/bin/jsub -N bot-stats -mem 5G -once -quiet /bin/bash /data/project/.../bot.stats.sh
botnick="Emijrpbot"
cd /data/project/emijrpbot/wikidata

echo "SELECT rev_comment FROM revision WHERE rev_user_text='$botnick';" > bot.stats.query
sql wikidata < bot.stats.query > bot.stats.sql

edits=$(wc -l bot.stats.sql | cut -d" " -f1)
echo "edits=$edits" | tee bot.stats.txt

labels=$(grep "BOT - Adding label" bot.stats.sql | grep -ioE "[0-9]+ language" | cut -d" " -f1 | awk "{ sum += \$1 } END { print sum }")
echo "labels=$labels" | tee -a bot.stats.txt

descriptions=$(grep "BOT - Adding description" bot.stats.sql | grep -ioE "[0-9]+ language" | cut -d" " -f1 | awk "{ sum += \$1 } END { print sum }")
echo "descriptions=$descriptions" | tee -a bot.stats.txt

aliases=$(grep -iE "BOT - Adding [0-9]+ alias" bot.stats.sql | grep -ioE "[0-9]+ alias" | cut -d" " -f1 | awk "{ sum += \$1 } END { print sum }")
echo "aliases=$aliases" | tee -a bot.stats.txt

claims=$(grep -iE "BOT - Adding [0-9]+ claim" bot.stats.sql | grep -ioE "[0-9]+ claim" | cut -d" " -f1 | awk "{ sum += \$1 } END { print sum }")
echo "claims=$claims" | tee -a bot.stats.txt

sitelinks=$(grep -iE "BOT - Adding [0-9]+ sitelink" bot.stats.sql | grep -ioE "[0-9]+ sitelink" | cut -d" " -f1 | awk "{ sum += \$1 } END { print sum }")
echo "sitelinks=$sitelinks" | tee -a bot.stats.txt

items=$(grep -ic "BOT - Creating item" bot.stats.sql)
echo "items=$items" | tee -a bot.stats.txt

python3 bot.stats.py
