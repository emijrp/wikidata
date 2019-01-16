#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2019 emijrp <emijrp@gmail.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gzip
import mwxml
import os
import re
import sys
import time

def main():
    botnick = "Emijrpbot"
    path = "/data/project/emijrpbot/bot-stats/"
    dumpfilename = sys.argv[1]
    n = int(dumpfilename.split('-history')[1].split('.xml')[0])
    dump = mwxml.Dump.from_file(gzip.open(dumpfilename))
    outputfile = "bot.stats.dump.output.%d" % (n)
    print(dump.site_info.name, dump.site_info.dbname)
    c = 0
    t1 = time.time()
    edits = 0
    aliases = 0
    claims = 0
    descriptions = 0
    labels = 0
    references = 0
    sitelinks = 0
    items = 0
    for page in dump:
        for revision in page:
            #print(revision.id)
            
            if revision.user and revision.user.text == botnick:
                #print(revision.comment)
                m = re.findall(r"(?i)BOT - Adding ([0-9]+) alias", revision.comment)
                aliases += m and int(m[0]) or 0
                m = re.findall(r"(?i)BOT - Adding ([0-9]+) claim", revision.comment)
                claims += m and int(m[0]) or 0
                m = re.findall(r"(?i)BOT - Adding descriptions? \(([0-9]+) languages?\)", revision.comment)
                descriptions += m and int(m[0]) or 0
                m = re.findall(r"(?i)BOT - Adding labels? \(([0-9]+) languages?\)", revision.comment)
                labels += m and int(m[0]) or 0
                m = re.findall(r"(?i)BOT - Adding ([0-9]+) reference", revision.comment)
                references += m and int(m[0]) or 0
                m = re.findall(r"(?i)BOT - Adding ([0-9]+) sitelink", revision.comment)
                sitelinks += m and int(m[0]) or 0
                m = re.findall(r"(?i)(BOT - Creating item)", revision.comment)
                items += m and 1 or 0
                edits += 1
            
            c += 1
            """
            if c % 1000 == 0:
                print(1000/(time.time()-t1), edits, aliases, claims, descriptions, labels, references, sitelinks, items)
                t1 = time.time()
            """
    with open("%s%s" % (path, outputfile), 'w') as f:
        output = "aliases=%d\nclaims=%d\ndescriptions=%d\nlabels=%d\nreferences=%d\nsitelinks=%d\nitems=%d\nedits=%d\n" % (aliases, claims, descriptions, labels, references, sitelinks, items, edits)
        f.write(output)

if __name__ == "__main__":
    main()
