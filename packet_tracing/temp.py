"""
__author__: Jamin Becker (jamin@packettotal.com)
"""

import os
import sys
import time
import socket
import logging
import pathlib
import warnings
from hashlib import md5


import psutil
import pyshark
import progressbar
from magic import from_buffer
from terminaltables import AsciiTable
from packettotal_sdk.packettotal_api import PacketTotalApi


from honeybot.lib import const


def capture_on_interface(interface, name, timeout=60):
    """
    :param interface: The name of the interface on which to capture traffic
    :param name: The name of the capture file
    :param timeout: A limit in seconds specifying how long to capture traffic
    """

    if timeout < 15:
        logger.error("Timeout must be over 15 seconds.")
        return
    if not sys.warnoptions:
        warnings.simplefilter("ignore")
    start = time.time()
    widgets = [
        progressbar.Bar(marker=progressbar.RotatingMarker()),
        ' ',
        progressbar.FormatLabel('Packets Captured: %(value)d'),
        ' ',
        progressbar.Timer(),
    ]
    progress = progressbar.ProgressBar(widgets=widgets)
    capture = pyshark.LiveCapture(interface=interface, output_file=os.path.join('tmp', name))
    pcap_size = 0
    for i, packet in enumerate(capture.sniff_continuously()):
        progress.update(i)
        if os.path.getsize(os.path.join('tmp', name)) != pcap_size:
            pcap_size = os.path.getsize(os.path.join('tmp', name))
        if not isinstance(packet, pyshark.packet.packet.Packet):
            continue
        if time.time() - start > timeout:
            break
        if pcap_size > const.PT_MAX_BYTES:
            break
    capture.clear()
    capture.close()
    return pcap_size


def check_auth():
    home = str(pathlib.Path.home())
    key = ''
    auth_path = os.path.join(home, 'honeybot.auth')
    if not os.path.exists(auth_path):
        print('HoneyBot requires a PacketTotal API key.')
        print('Signup at: \n\t: https://packettotal.com/api.html\n')
    else:
        key = open(auth_path, 'r').read()
    while PacketTotalApi(key).usage().status_code == 403:
        print('Invalid API Key. Try again.')
        key = input('API Key: ')
        open(auth_path, 'w').write(key)

    return open(auth_path, 'r').read()


def get_filepath_md5_hash(file_path):
    """
    :param file_path: path to the file being hashed
    :return: the md5 hash of a file
    """
    with open(file_path, 'rb') as afile:
       return get_file_md5_hash(afile)


def get_str_md5_hash(s):
    return md5(str(s).encode('utf-8')).hexdigest()


def get_mac_address_of_interface(interface):
    """
    :param interface: The friendly name of a network interface
    :return: the MAC address associated with that interface
    """
    for k,v in psutil.net_if_addrs().items():
        if interface == k:
            for item in v:
                try:
                    if item.family == socket.AF_LINK:
                        return item.address
                except AttributeError:
                    # Linux
                    if item.family == socket.AF_PACKET:
                        return item.address
    return None


def gen_unique_id(interface):
    """
    Generates a unique ID based on your MAC address that will be used to tag all PCAPs uploaded to PacketTotal.com
    This ID can be used to search and view PCAPs you have uploaded.

    :param interface: The friendly name of a network interface
    :return: A unique id
    """
    mac_address = get_mac_address_of_interface(interface)
    if mac_address:
        return get_str_md5_hash(get_str_md5_hash(mac_address))[0:15]
    return None


def get_file_md5_hash(fh):
    """
    :param fh: file handle
    :return: the md5 hash of the file
    """
    block_size = 65536
    md5_hasher = md5()
    buf = fh.read(block_size)
    while len(buf) > 0:
        md5_hasher.update(buf)
        buf = fh.read(block_size)
    return md5_hasher.hexdigest()


def get_network_interfaces():
    """
    :return: A list of valid interfaces and their addresses
    """
    return psutil.net_if_addrs().items()


def is_packet_capture(bytes):
    """
    :param bytes: raw bytes
    :return: True is valid pcap or pcapng file
    """
    result = from_buffer(bytes)
    valid = "pcap-ng" in result or "tcpdump" in result or "NetMon" in result or 'pcap capture file' in result
    return valid


def mkdir_p(path):
    """
    :param path: Path to the new directory to create
    """

    pathlib.Path(path).mkdir(parents=True, exist_ok=True)


def listen_on_interface(interface, timeout=60):
    """
    :param interface: The name of the interface on which to capture traffic
    :return: generator containing live packets
    """

    start = time.time()
    capture = pyshark.LiveCapture(interface=interface)

    for item in capture.sniff_continuously():
        if timeout and time.time() - start > timeout:
            break
        yield item


def print_network_interaces():
    """
    :return: Prints a human readable representation of the available network interfaces
    """

    for intf, items in get_network_interfaces():
        table = [["family", "address", "netmask", "broadcast", "ptp"]]
        for item in items:
            family, address, netmask, broadcast, ptp = item
            table.append([str(family), str(address), str(netmask), str(broadcast), str(ptp)])
        print(AsciiTable(table_data=table, title=intf).table)
        print('\n')


def print_analysis_disclaimer():
    print("""
        WARNING: Analysis will result in the network traffic becoming public at https://packettotal.com.
        
        ADVERTENCIA: El an??lisis har?? que el tr??fico de la red se haga p??blico en https://packettotal.com.
        
        WARNUNG: Die Analyse f??hrt dazu, dass der Netzwerkverkehr unter https://packettotal.com ??ffentlich wird.
        
        ????????????????????????????. ???????????? ???????????????? ?? ????????, ?????? ?????????????? ???????????? ???????????? ?????????????????????????? ???? https://packettotal.com.
        
        ?????????????????????: ???????????????????????? ?????? ?????????????????? ????????????????????? ????????????????????? https://packettotal.com ?????? ??????????????????????????? ?????? ???????????????
        
        ???????????????????????????????????????https://packettotal.com?????????
        
        ??????????????????????????????????????????????????????????????????https://packettotal.com????????????????????????
        
        tahdhir: sayuadiy altahlil 'iilaa 'an tusbih harakat murur alshabakat eamat ealaa https://packettotal.com

    """)

    answer = input('Continue? [Y/n]: ')
    if answer.lower() == 'n':
        exit(0)


def print_pt_ascii_logo():
    """
    :return: Prints a PacketTotal.com (visit https://PacketTotal.com!)
    """

    logo = """
                                                           ,,*****,                 ,****,
                                                   ****/**,  /              ,*//*,
                                                   ****/**,  ,,**********,. ******
                            ..  .,*****,  ..       ********  ************,.   .
                    .  .,,***,  ,******, .,***,,..           *****////***,  ,***,
                 ...  ,******,  ,******, .,********          *****////***,. ****,
            .,,****,  ,******,  ,******,  ,********          ************,  .///
             /////* // ////// /( ////// /( */////             ************
    ****,. ,,******.  ,******.  ,******,  .******,,.,******,.               *
    *****, ********,  ,******,  ,******, .,********.,********      ,*******,
    *****, ********,  ,******,  ,******, .,********.,********      ****//**,
    *****, /*******,  ,*******  *//////*  ********/ ,********      ****//**,
    ////* / .////// ((.(((((( ## (((((( (& /(((((  % //////        ,******** .
    ,,,,,. ,,,,,,,,.  ,,*****,  ,******,  ,*****,,,..,,,,,,,. .,,,,,,
    *****, /*******,  *//////*  *//////* .*//////*/.*********,,*****,
    *****, /*******,  *//////*  (.     (  *////////.*********,,******
    *****, /********  */////(* ..,,,,,,..  (/////// ********* *******
    ////* / ,/((((/ #@,####*..,**********,. /####. & /(((((. @ *////
    ,,,,,. ..,,,,*,,  ,**,  ,*****////*****,./***,. ,,,,,,,.. .,,,,,
     ,***, /*****//*  */// .,***//(##((/****, /////,*//******,,***,
     ****, /*****//*  *//* ,****/(%&&%(//**,, ////(,*//******,,****
     ****, /*****//*  *//*  ,***//(##(//***** *///( *//******.***,
      *** ( **///// #@//((. ******////****** /(((* @ //////*   **,
       ,,. ..,,,,,,,  ,****,. ************ .,****,. ,,,,,,,.. ,,*
        *, /********  *//////,   ,****,   ,////////.*********,,*
         * /*******,  *//////*  ,******, .*////////.*********,,
           /********  *//////*  *//////*  *//////*/ *********
            *******,# ////////# ////////#  //////*   /******
             ,,,,,..((.,,,,,,.(#.,,,,,,.(#.,,,,,,..(..,,,,,
            * *****,  ,******,  *//////* .,*******/.,*****
                ***,  ,******,  ,******, .,********.,*** /
               * ,*,  ,******,  ,******,  ,********.,*  .
                      *******/  *******/  ,*******    ,
                       ,,,,,..// .,,,,..// .,,,,,
                      / .****,  ,******, .,****, /
                         / ***  ,******,  ***
                                ********   #
    
                                    - honeybot: Capture and analyze network traffic; powered by PacketTotal.com
                                               : VERSION: {}
    """.format(const.VERSION)
    print(logo)



# Setup Logging

mkdir_p('logs/')
mkdir_p('tmp/')
logger = logging.getLogger('honeybot.utils')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('logs/honeybot.log')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)