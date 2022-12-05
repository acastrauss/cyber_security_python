import zipfile
import optparse
from threading import Thread


def extractFile(zFile, password: str):
    try:
        zFile.extractall(pwd=password.encode('utf-8'))
        print(f"Password is:{password}")
    except Exception as e:
        print(e)
        pass

def main():
    parser = optparse.OptionParser("usage%prog " + "-f <zipfile> -d <dictionary>")
    parser.add_option('-f', dest='zname', type='string', help='specify zip file')
    parser.add_option('-d', dest='dname', type='string', help='specify passwords file')
    (options, args) = parser.parse_args()
    if (options.zname == None) | (options.dname == None):
        print(parser.usage)
        exit(0)
    else:
        zname = options.zname
        dname = options.dname
    
    zFile = zipfile.ZipFile(zname)
    with open(dname, 'r') as f:
        for line in f.readlines():
            l = line.strip()
            t = Thread(target=extractFile, args=(zFile, l))
            t.start()

if __name__ == '__main__':
    main()