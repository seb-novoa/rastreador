import paho.mqtt.client as paho
import datetime

class Panel:
    def __init__(self, topic, tiempoDeSalida, estado):
        self.topic  =   topic
        self.tiempoDeSalida = tiempoDeSalida
        self.estado =   estado
        self.encendido   =   True
        self.arribo      =   False
        self.detenido    =   False
        self.tiempo_atraso = tiempoDeSalida

    def tiempo_de_llegada(cronometro):
        pass

    def publicador(self, mqttPublish, topic, msg):
        print(self.topic + topic)
        mqttPublish.publish(self.topic + topic, msg, 0)

