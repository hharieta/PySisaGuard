import pyshark
import csv
import json
import datetime
import joblib
from typing import Dict
import pandas as pd
from tensorflow.keras.models import load_model

model = load_model('models/sisa_model.h5')
scaler = joblib.load('models/sisa_scaler.pkl')

print

def capture_live_packets(interface: str = None) -> object:
    capture = pyshark.LiveCapture(interface=interface)
    for packet in capture.sniff_continuously():
        yield packet


def extract_packet_data(packet: object) -> Dict[str, str]:
    try:
        # hieghest_layer = packet.highest_layer
        protocol = packet.transport_layer
        src_addr = packet.ip.src
        dst_addr = packet.ip.dst
        origin_port = packet[packet.transport_layer].srcport
        destination_port = packet[packet.transport_layer].dstport
        timestamp = packet.sniff_timestamp
        # stream_value = packet.tcp.stream
        # ack = packet[packet.transport_layer].ack
        # length = packet.length


        return {
            'Timestamp': timestamp,
            'Protocol': protocol,
            'Source Port': origin_port,
            'Destination Port': destination_port,
            'Source IP Address': src_addr,
            'Destination IP Address': dst_addr,
        }

    except AttributeError:
        return None
    

def detect_attacks(features, model) -> object:

    prediction = model.predict(features)
    
    return prediction

with open(f'captures/{datetime.datetime.now()}.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Timestamp', 'Protocol', 'Source Port', 'Destination Port', 'Source IP Address', 'Destination IP Addres', 'Status'])
    
    for packet in capture_live_packets(interface='en7'):

        features = extract_packet_data(packet)
        if features:
            
            features_to_csv = features.copy()
            sr_ip_split = features['Source IP Address'].split('.')
            ds_ip_split = features['Destination IP Address'].split('.')
            features_to_model = {
                'Source Port': features['Source Port'],
                'Destination Port': features['Destination Port'],
                'Source IP Address 1': sr_ip_split[0],
                'Source IP Address 2': sr_ip_split[1],
                'Source IP Address 3': sr_ip_split[2],
                'Source IP Address 4': sr_ip_split[3],
                'Destination IP Address 1': ds_ip_split[0],
                'Destination IP Address 2': ds_ip_split[1],
                'Destination IP Address 3': ds_ip_split[2],
                'Destination IP Address 4': ds_ip_split[3]

            }
            features_to_model = pd.DataFrame([features_to_model])
            features_to_model = features_to_model.values.reshape(1, 10)

            features_to_model = scaler.transform(features_to_model)


            prediction = detect_attacks(features_to_model, model)
            features_to_csv["Status"] = prediction[0][0]
            writer.writerow(list(features_to_csv.values()))
            f.flush()
            
            if prediction == 1:  
                print("Sospechoso:", features)
                # make some action
            else:
                print("No sospechoso: ", features)



