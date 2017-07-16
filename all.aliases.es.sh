#!/bin/bash
for i in {0..9}
do
   /usr/bin/jsub -N aliases$i -mem 1G -once -quiet python3 /data/project/emijrpbot/wikidata/all.aliases.es.py $i
done
