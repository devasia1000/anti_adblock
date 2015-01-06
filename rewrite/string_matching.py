from libmproxy.protocol.http import decoded

log_file = ''
filter_list = []

def string_matching_boyer_moore_horspool(text='', pattern=''):
    """
    Returns positions where pattern is found in text
    See http://en.wikipedia.org/wiki/Boyer%E2%80%93Moore%E2%80%93Horspool_algorithm for an explanation on how
    this algorithm works.

    O(n)
    Performance: ord() is slow so we shouldn't use it here
    Example: text = 'ababbababa', pattern = 'aba'
                     string_matching_boyer_moore_horspool(text, pattern) returns [0, 5, 7]
    @param text text to search inside
    @param pattern string to search for
    @return list containing offsets (shifts) where pattern is found inside text
    """

    m = len(pattern)
    n = len(text)
    offsets = []
    if m > n:
        return offsets
    skip = []
    for k in range(256):
        skip.append(m)
    for k in range(m-1):
        skip[ord(pattern[k])] = m - k - 1
    skip = tuple(skip)
    k = m - 1
    while k < n:
        j = m - 1; i = k
        while j >= 0 and text[i] == pattern[j]:
            j -= 1
            i -= 1
        if j == -1:
            offsets.append(i + 1)
        k += skip[ord(text[k])]

    return offsets

def start(context, argv):
    global log_file
    global filter_list

    log_file = open("log.txt", "w")

    fs = open("easylist.txt")
    for line in fs:
        filter_list.append(line.rstrip())

def response(context, flow):
    global log_file
    global filter_list

    with decoded(flow.response):
        for rule in filter_list:
            #print 'Trying out ' + rule
            result = string_matching_boyer_moore_horspool(flow.response.content, rule)
            for res in result:
                #log_file.write(str(res) + '\n')
                #log_file.flush()
                print str(flow.response.content)[res:res+10]