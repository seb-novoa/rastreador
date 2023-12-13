import paho.mqtt.client as paho
import datetime

class Panel:
    def __init__(self, topic, tiempoDeSalida, estado):
        self.topic  =   topic
        self.tiempoDeSalida = tiempoDeSalida
        self.estado =   estado
        self.encendido   =   True
        self.arribo      =   False
        self.atrasado    =   False
        self.tiempo_atraso = tiempoDeSalida
        self.tiempo_atraso_cal = tiempoDeSalida

    def tiempo_de_llegada(cronometro):
        pass

    def publicador(self, mqttPublish, topic, msg):
        mqttPublish.publish(self.topic + topic, msg, 0)

    def mostrar_calculando(self, mqttPublish):
        mqttPublish.publish(self.topic + "/llegada", "Calculando", 0)

