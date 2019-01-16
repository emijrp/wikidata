#!/bin/bash

cd /data/project/emijrpbot/bot-stats/
rm bot.stats.dump.output.*

nfiles=0
for dump in /public/dumps/public/wikidatawiki/latest/wikidatawiki-latest-stub-meta-history[0-9]*.xml.gz; do
    n=(${dump//y/ })
    n=${n[1]}
    n=(${n//./ })
    n=${n[0]}
    echo $dump
    /usr/bin/jsub -N botstats$n -mem 500M -once -quiet /bin/bash /data/project/emijrpbot/bot-stats/bot.stats.dump.core.sh $dump
    nfiles=$((nfiles+1))
done

nfiles2=0
sleep=60
while [ "$nfiles" -ne "$nfiles2" ]
do
    nfiles2=( `ls -l /data/project/emijrpbot/bot-stats/bot.stats.dump.output.* 2> /dev/null | wc -l` )
    sleep $sleep
    echo "Waiting $sleep seconds..."
    echo "$nfiles2 of $nfiles done"
done

cd /data/project/emijrpbot/bot-stats/
python /data/project/emijrpbot/bot-stats/bot.stats.dump2.py
echo "OK!"
cat /data/project/emijrpbot/bot-stats/bot.stats.txt
cp /data/project/emijrpbot/bot-stats/bot.stats.txt /data/project/emijrpbot/wikidata/bot.stats.txt
python /data/project/emijrpbot/wikidata/bot.stats.py
