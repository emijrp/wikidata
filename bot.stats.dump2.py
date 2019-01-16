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

import glob

def main():
    stats = {}
    filenames = glob.glob("bot.stats.dump.output.*")
    for filename in filenames:
        with open(filename, "r") as f:
            raw = f.read()
            for l in raw.splitlines():
                x, y = l.strip().split('=')
                x = x.strip().lower()
                y = y.strip()
                if x in stats:
                    stats[x] += y and int(y) or 0
                else:
                    stats[x] = y and int(y) or 0
    with open("bot.stats.txt", "w") as f:
        for k, v in stats.items():
            f.write("%s=%s\n" % (k, v))

if __name__ == "__main__":
    main()
