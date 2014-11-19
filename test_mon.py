import sys
import urllib2

def get_url_nofollow(url):
    try:
        response = urllib2.urlopen(url)
        code = response.getcode()
        return code
    except urllib2.HTTPError as e:
        return e.code
    except:
        return 0

def main():
    urls = {}
    
    for line in sys.stdin.readlines():
        line = line.strip()
        if line not in urls:
            sys.stderr.write("+ checking URL: %s\n" % line)
            urls[line] = {'code': get_url_nofollow(line), 'count': 1}
            sys.stderr.write("++ %s\n" % str(urls[line]))
        else:
            urls[line]['count'] = urls[line]['count'] + 1
    
    for url in urls:
        if urls[url]['code'] != 200:
            print "%d\t%d\t%s" % (urls[url]['count'], urls[url]['code'], url)

if __name__ == "__main__":
    main()
