# -*- coding: utf-8 -*-

from adblockparser import AdblockRules
from libmproxy.protocol.http import decoded
from urlparse import urlparse

import hashlib
import re

url_dict = dict()
adblock_rules = ''
log_file = ''
hostname = 'destructoid.com'
urlRegex = ".src[\s]*=[\s]*['\"]([^'\"]+)['\"]"
delimiter = '--;*;*;*--'
domShield = """<script>

function block(node) {
    if (   (node.nodeName == 'link' && node.href == 'data:text/css,') // new style
        || (node.nodeName == 'style' && node.innerText.match(/^\/\*This block of style rules is inserted by AdBlock/)) // old style
        ) {
        alert("Going to block");
        node.parentElement.removeChild(node);
    }
}

document.addEventListener("DOMContentLoaded", function() {
    document.addEventListener('DOMNodeInserted', function(e) {
        // disable blocking styles inserted by AdBlock
        block(e.target);
    }, false);
}, false);

</script>
"""

def start(context, argv):
    global log_file
    global adblock_rules
    global url_dict
    global hostname
    global urlRegex

    log_file = open("log.txt", "w")

    filter_list = []
    fs = open("easylist.txt")
    for line in fs:
        filter_list.append(line.rstrip())

    adblock_rules = AdblockRules(filter_list)

def removeAds(string, regex, useRegex):
    # 1. Use regex to extract urls of the form http:// and https://
    # 2. Replace URL with hash
    # 3. Use regex to extract urls of general forms on string modified by above
    # 4. Replace URL with hash
    # Source: http://daringfireball.net/2010/07/improved_regex_for_matching_urls

    # TODO(devasia) : improve regex matching for URLs

    global log_file
    global adblock_rules
    global url_dict
    global hostname
    global urlRegex
    global delimiter

    modified = False
    generalUrlList = []

    if useRegex == True:
        generalUrlList.extend(re.findall(urlRegex, string))
        #log_file.write('size of generalUrlList ' + str(len(generalUrlList)) + '\n')

    else:
        generalUrlList.append(string)

    for generalUrl in generalUrlList:
        #log_file.write('checking ' + generalUrl + '\n')
        if adblock_rules.should_block(generalUrl) == True:
            modified = True

            hash_dig = hashlib.sha256(str(generalUrl)).hexdigest()
            changedUrl = 'http://' + hostname + '/' + hash_dig + delimiter

            parsed_uri = urlparse(generalUrl)
            domain = '{uri.netloc}'.format(uri=parsed_uri)

            url_dict[changedUrl] = (generalUrl, domain)   # save transformation into dict
            string = string.replace(generalUrl, changedUrl)

            #log_file.write(generalUrl + '  -->>  ' + changedUrl + '\n')

    return string, modified

def response(context, flow):
    global log_file
    global adblock_rules
    global url_dict
    global hostname
    global urlRegex
    global domShield

    with decoded(flow.response):
        # anonymize request


        # anonymize headers

        #inject DOM shield
        flow.response.content = flow.response.content.replace('<head>', '<head>' + domShield)

        # anonymize content
        #flow.response.content, modified = removeAds(flow.response.content, urlRegex, True)

        pass

def request(context, flow):
    global log_file
    global adblock_rules
    global url_dict
    global hostname
    global delimiter

    """host_val = flow.request.headers['Host'][0]
    if 'doubleclick' in host_val:
        log_file.write(str(flow.request.path) + '\n')
        log_file.write(str(flow.request.headers) + '\n')
        log_file.write('\n\n')"""

    # restore GET request
    if delimiter in flow.request.path:
        #log_file.write('going to restore : ' + flow.request.path + '\n')
        temp = flow.request.path.split(delimiter)

        (restoredUrl, restoredHostHeader) =  url_dict['http://' + hostname + temp[0] + delimiter]

        restoredPath = urlparse(restoredUrl).path + ';' + urlparse(restoredUrl).params + temp[1]

        #log_file.write('replaced with : ' + restoredPath + '\n')
        flow.request.path = restoredPath

        # restore host header
        flow.request.headers['Host'] = [restoredHostHeader]
        flow.request.host = restoredHostHeader

        #log_file.write(str(flow.request.path) + '\n')
        #log_file.write(str(flow.request.headers) + '\n')
        #log_file.write('\n\n')
