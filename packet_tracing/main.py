from struct import pack
import dpkt
import socket
import pygeoip
from requests import get
import pyshark

gi = pygeoip.GeoIP("./GeoLiteCity/GeoLiteCity.dat")
my_public_ip = get('https://api.ipify.org').content.decode('utf8')

def retKML(dst_ip, src_ip):
    dst = gi.record_by_name(dst_ip)
    src = gi.record_by_name(my_public_ip)
    try:
        dstLongitude = dst['longitude']
        dstLatitude = dst['latitude']
        srcLongitude = src['longitude']
        srcLatitude = src['latitude']
        kml = (
           '<Placemark>\n'
            '<name>%s</name>\n'
            '<extrude>1</extrude>\n'
            '<tessellate>1</tessellate>\n'
            '<styleUrl>#transBluePoly</styleUrl>\n'
            '<LineString>\n'
            '<coordinates>%6f,%6f\n%6f,%6f</coordinates>\n'
            '</LineString>\n'
            '</Placemark>\n'
        )%(dst_ip, dstLongitude, dstLatitude, srcLongitude, srcLatitude 
        )
        return kml
    except:
        pass

def plotIps(pcap: dpkt.pcap.Reader):
    kmlPts = ''
    for (ts, buf) in pcap:
        try:
            eth = dpkt.ethernet.Ethernet(buf)
            ip = eth.data
            src = socket.inet_ntoa(ip.src)
            dst = socket.inet_ntoa(ip.dst)
            kmlPts += retKML(dst, src)
        except:
            pass
    return kmlPts

def capture_packets():
    # all interfaces is when None is by default
    capture = pyshark.LiveCapture(
        output_file='packages1.pcap'
    )

    capture.interfaces = capture.interfaces[:-2]
    packetMaxCnt = 30
    capture.sniff(packet_count=packetMaxCnt)
    local = '127.0.0.1'
    kmlpts = ''

    src = gi.record_by_name(my_public_ip)
    print(capture)
    packtCnt = 0
    for packet in capture.sniff_continuously():
        if(hasattr(packet, 'ip')):
            if (packet.ip.dst != local):
                print(packet.ip.dst)
                packtCnt +=1
                print(f"Cnt:{packtCnt}")
                if (packtCnt >= packetMaxCnt):
                    break
                
                dst = gi.record_by_name(packet.ip.dst)
                try:
                    dstLongitude = dst['longitude']
                    dstLatitude = dst['latitude']
                    srcLongitude = src['longitude']
                    srcLatitude = src['latitude']
                    kml = (
                    '<Placemark>\n'
                        '<name>%s</name>\n'
                        '<extrude>1</extrude>\n'
                        '<tessellate>1</tessellate>\n'
                        '<styleUrl>#transBluePoly</styleUrl>\n'
                        '<LineString>\n'
                        '<coordinates>%6f,%6f\n%6f,%6f</coordinates>\n'
                        '</LineString>\n'
                        '</Placemark>\n'
                    )%(packet.ip.dst, dstLongitude, dstLatitude, srcLongitude, srcLatitude 
                    )
                    kmlpts += kml

                except:
                    pass
                
    capture.close()
    return kmlpts

def main():
    
    kmlheader = '<?xml version="1.0" encoding="UTF-8"?> \n<kml xmlns="http://www.opengis.net/kml/2.2">\n<Document>\n'\
                '<Style id="transBluePoly">' \
                '<LineStyle>' \
                '<width>1.5</width>' \
                '<color>501400E6</color>' \
                '</LineStyle>' \
                '</Style>'
    kmlfooter = '</Document>\n</kml>\n'
    kmldoc = kmlheader + capture_packets() + kmlfooter

    with open('kml_maps.kml', 'w') as f:
        f.write(kmldoc)

if __name__ == "__main__":
    main()