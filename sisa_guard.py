import pyshark
import csv
import json
import os
import datetime
import joblib
import numpy as np
import pandas as pd
from typing import Dict
from dotenv import load_dotenv
from send_email import send_mail
from tensorflow.keras.models import load_model

if os.getenv('ENV') == 'DEV':
    load_dotenv()


model = load_model('models/sisa_model_v4.h5')
scaler = joblib.load('models/sisa_scaler_v4.joblib')
json_file = f'captures/{datetime.datetime.now()}.json'
file_csv = f'captures/{datetime.datetime.now()}.csv'

data_list = []

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

def default_serializer(o) -> str:
    if isinstance(o, np.float32):
        return o.__str__()
    
    raise TypeError(f"Object of type '{o.__class__.__name__}' is not JSON serializable")


def write_to_json(data: Dict[str, str], filename: str) -> None:

    json_data = []

    if os.path.isfile(filename):
        with open(filename, 'r') as f:
            json_data = json.load(f)

    json_data.append(data)

    with open(filename, 'w') as f:
        json.dump(json_data, f, indent=4, default=default_serializer)


def write_to_csv(data: Dict[str, str], filename: str) -> None:
    f_exists = os.path.isfile(filename)
    print(data)

    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        if not f_exists:
            writer.writerow(['Timestamp', 'Protocol', 'Source Port', 'Destination Port', 'Source IP Address', 'Destination IP Addres', 'Status'])
        else:
            row = [str(value) for value in data.values()]
            writer.writerow(row)
        f.flush()
    
for packet in capture_live_packets(interface='en7'):

    features = extract_packet_data(packet)
    if features:
        
        features_to_write = features.copy()
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
        features_to_write["Status"] = prediction[0][0]
        print("Features: ", features_to_write)
        # write_to_csv(features_to_write, file_csv)
        write_to_json(features_to_write, json_file)
        
        if prediction >= 0.8:  
            print("Tráfico Sospechoso:", features)
            send_mail.send_email()
            # make some action
        else:
            print("Tráfico no sospechoso: ", features)



