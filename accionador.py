import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("conexion con mqtt" + str(rc))
    client.subscribe("topic/accion")

def on_message(client, userdata, msg):
    if(msg.payload.decode('utf8') == 'normal'):
        print("estamos")
    if(msg.payload.decode('utf8') == 'atraso'):
        print("obvio")
    

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("broker.hivemq.com", 1883, 60)
client.loop_forever()