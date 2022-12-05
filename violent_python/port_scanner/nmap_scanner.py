import nmap
import optparse

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

def nmapScan(tgtHost, tgtPort):
    try:
        nmScan = nmap.PortScanner()
        nmScan.scan(tgtHost, tgtPort)
        ports = nmScan[tgtHost]['tcp'].keys()
        for p in ports:
            print(f"{tgtHost} tcp/{p} {nmScan[tgtHost]['tcp'][p]['state']}")
    except Exception as e:
        print(f"Exception:{e}")

def main():
    # args = parse_cmd_line()
    # if args is None:
        # return

    for port in ['22-443']:
        print(f"port {port}")
        nmapScan('127.0.0.1', port)

if __name__ == '__main__':
    main()