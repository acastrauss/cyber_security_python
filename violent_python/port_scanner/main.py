
from multiprocessing import Semaphore
import optparse
from socket import *
from threading import Thread

def parse_cmd_line():
    parser = optparse.OptionParser('usage %prog' + '-H <target host>' + '-p <target port>')
    parser.add_option('-H', dest='tgtHost', type='string', help='specify target host')
    parser.add_option('-p', dest='tgtPort', type='string', help='specify target ports separated by comma')
    (options, args) = parser.parse_args()
    tgtHost = options.tgtHost
    tgtPorts = str(options.tgtPort).split(',')
    if (tgtHost == None) | (tgtPorts[0] == None):
        print(parser.usage)
        return None
    return (tgtHost, tgtPorts)

screenLock = Semaphore(value=1)

def connScan(tgtHost, tgtPort):
    try:
        connSckt = socket(AF_INET, SOCK_STREAM)
        connSckt.connect((tgtHost, tgtPort))
        connSckt.send('Dumb data\r\n'.encode('utf-8'))
        results = connSckt.recv(100)
        screenLock.acquire()
        print(f"{tgtHost}/tcp open at port {tgtPort}")
        print(f"Results: {results}")
    except Exception as e:
        screenLock.acquire()
        print(e)
        print(f"{tgtHost}/tcp closed at port {tgtPort}")
    finally:
        screenLock.release()
        connSckt.close()

def portScann(tgtHost, tgtPorts):
    try:
        tgtIp = gethostbyname(tgtHost)
    except:
        print(f"Cannot resolve {tgtHost}. Unknown host")
        return
    
    try:
        tgtName = gethostbyaddr(tgtIp)
        print(f"Scan results for:{tgtName[0]}")
    except Exception as e:
        print(e)
        print(f"Scan results for IP:{tgtIp}")
    
    setdefaulttimeout(1)

    for port in tgtPorts:
        print(f"Scanning port {port}")
        t = Thread(target=connScan, args=(tgtHost, int(port)))
        t.start()

def main():
    args = parse_cmd_line()
    if args is None:
        return
    portScann(args[0], args[1])

if __name__ == '__main__':
    main()