filter_list = []
fs = open("easylist.txt")
for line in fs:
    filter_list.append(line.rstrip())

link_list = []
fs2 = open("links.txt")
for line in fs2:
    link_list.append(line.rstrip())

from adblockparser import AdblockRules
rules = AdblockRules(filter_list)

for link in link_list:
    if rules.should_block(link) == True:
        print link
