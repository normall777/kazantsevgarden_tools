import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import json
import paho.mqtt.client as mqtt

cred = credentials.Certificate("/home/pi/kazantsevgarden/serviceAccountKey.json")
database_url = "https://kazantsevgarden-default-rtdb.europe-west1.firebasedatabase.app"
default_app = firebase_admin.initialize_app(cred,  {"databaseURL": database_url})
ref = db.reference("/Measurments/Garden")
modules = { 
        "cat" : ["light", "water"], 
        "owl" : ["temp", "hum", "person"]
        }

#print(ref.get())
def on_connect(client, userdata, flags, rc):
    client.subscribe("/firebase")

def on_message(client, userdata, msg):
    timepoint = datetime.utcnow().strftime("%Y/%m/%d/%H:%M")
    #timepoint = datetime.utcnow().strftime("%Y%m%d %H:%M")
    print(msg.payload.decode("utf-8"))
    try:
        splitted_message = msg.payload.decode("utf-8").split(" ")
        module_name = splitted_message.pop(0)
        print(module_name)
        if (len(modules[module_name]) != len(splitted_message)):
            print("Error in data for modul {}".format(module_name))
            return

    except:
        print("ERROR IN CHECK MODULE DATA")
        return
    print(splitted_message)
    child_ref = ref.child(timepoint)
    try:
        result_dict = {}
        for i in range(len(modules[module_name])):
            result_dict.update({modules[module_name][i]:int(splitted_message[i])})
        print(result_dict)
        child_ref.set({
            module_name : 
                result_dict
            })

    except:
        print("Error of setting data to db")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.loop_forever()
