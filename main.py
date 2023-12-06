from Paneles import Panel
import paho.mqtt.client as paho
import sys
import datetime

# #   Desfase del tiempo.
# def timer(off):
#     offTimer    =   datetime.timedelta(seconds=off)
# offTimer    =   0



## Conectando a Broker
client  =   paho.Client()
if(client.connect("broker.hivemq.com", 1883, 60)    !=  0):
    print("No hay conexion con el broker")
    sys.exit(-1)

## Se definen los tiempo de salida 
### A la hora actual se le suman un tiempo para representar una salida de la estacion.
control1    =   Panel("control1",  datetime.datetime.now() + datetime.timedelta(seconds=30),   True)
control2    =   Panel("control2",  datetime.datetime.now() + datetime.timedelta(seconds=60),  True)
control3    =   Panel("control3",  datetime.datetime.now() + datetime.timedelta(seconds=120),  True)

### Crear lista de objetos
paneles = []
paneles.append(control1)
paneles.append(control2)
paneles.append(control3)


## Se envia al HMI los tiempos calculados
control1.publicador(client, "/salida", control1.tiempoDeSalida.strftime("%m/%d/%Y, %H:%M:%S"))
control2.publicador(client, "/salida", control2.tiempoDeSalida.strftime("%m/%d/%Y, %H:%M:%S"))
control3.publicador(client, "/salida", control3.tiempoDeSalida.strftime("%m/%d/%Y, %H:%M:%S"))

#control1.arribo = True

#  Definir el estado de los servicios
for panel in paneles:
    if((datetime.datetime.now()   -   panel.tiempo_atraso).total_seconds()   <=  0   and panel.encendido):
        print('green flag')
        panel.publicador(client, "/estado", "A tiempo")
        panel.publicador(client, "/semaforo", "green")
        panel.publicador(client, "/llegada", panel.tiempoDeSalida.strftime("%m/%d/%Y, %H:%M:%S"))

    elif(panel.arribo):
        print('black flag')
        panel.encendido = False
        panel.publicador(client, "/estado", "Apagado")
        panel.publicador(client, "/semaforo", "black")

    elif((datetime.datetime.now()   -   panel.tiempo_atraso).total_seconds()   >  180):
        print('red flag')
        panel.publicador(client, "/estado", "Servicio suprimido")
        panel.publicador(client, "/semaforo", "red")
        panel.publicador(client, "/llegada", panel.tiempoDeSalida.strftime("%m/%d/%Y, %H:%M:%S"))
        tiempo_delta = (datetime.datetime.now()   -   panel.tiempoDeSalida).total_seconds()
        for paneles_encendidos in paneles:
            if(paneles_encendidos.encendido and paneles_encendidos.topic  !=  panel.topic):
                paneles_encendidos.tiempo_atraso   -= datetime.timedelta(seconds=tiempo_delta)
        
    else:
        print('yellow flag')
        panel.publicador(client, "/estado", "Servicio atrasado")
        panel.publicador(client, "/semaforo", "yellow")
        panel.publicador(client, "/llegada", panel.tiempoDeSalida.strftime("%m/%d/%Y, %H:%M:%S"))
        tiempo_delta = (datetime.datetime.now()   -   panel.tiempoDeSalida).total_seconds()
        for paneles_encendidos in paneles:
            if(paneles_encendidos.encendido and paneles_encendidos.topic  !=  panel.topic):
                paneles_encendidos.tiempo_atraso   -= datetime.timedelta(seconds=tiempo_delta)


#while((datetime.datetime.now()   -   control2.tiempoDeSalida).total_seconds()   <=  0):
 #   print((datetime.datetime.now()   -   control1.tiempoDeSalida).total_seconds() < 0)

