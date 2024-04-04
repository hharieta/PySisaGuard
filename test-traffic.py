import csv
import pyshark

def packet_callback(packet):
    try:
        hieghest_layer = packet.highest_layer
        protocol = packet.transport_layer
        src_addr = packet.ip.src
        dst_addr = packet.ip.dst
        origin_port = packet[packet.transport_layer].srcport
        destination_port = packet[packet.transport_layer].dstport
        stream_value = packet.tcp.stream
        ack = packet[packet.transport_layer].ack
        length = packet.length

        print(hieghest_layer, protocol, src_addr, dst_addr, origin_port, destination_port, stream_value, ack, length)
        writer.writerow([hieghest_layer, protocol, src_addr, dst_addr, origin_port, destination_port, stream_value, ack, length])
        
    except AttributeError:
        # No es un paquete IP
        pass

with open('test-traffic.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Highest Layer', 'Protocol', 'Source Address', 'Destination Address', 'Origin Port', 'Destination Port', 'Stream Value', 'Ack', 'Length'])

    capture = pyshark.LiveCapture(interface='en0')

    capture.apply_on_packets(packet_callback, packet_count=10000)

