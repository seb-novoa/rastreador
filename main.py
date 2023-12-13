from Paneles import Panel
import paho.mqtt.client as paho
import sys
import datetime
import time

# #   Desfase del tiempo.
# def timer(off):
#     offTimer    =   datetime.timedelta(seconds=off)
# offTimer    =   0


## Se definen los tiempo de salida 
### A la hora actual se le suman un tiempo para representar una salida de la estacion.
timeCheck   =   datetime.datetime.now()
control1    =   Panel("control1",  timeCheck + datetime.timedelta(seconds=10),   True)
control2    =   Panel("control2",  timeCheck + datetime.timedelta(seconds=30),  True)
control3    =   Panel("control3",  timeCheck + datetime.timedelta(seconds=60),  True)

control1.arribo = True
control2.arribo = True
control3.arribo = True

### Crear lista de objetos
paneles = []
paneles.append(control1)
paneles.append(control2)
paneles.append(control3)



## Conectando a Broker
client  =   paho.Client()

if(client.connect("broker.hivemq.com", 1883, 60)    !=  0):
    print("No hay conexion con el broker")
    sys.exit(-1)

client.publish("rastreador1/estatus", "OFFLINE", 0)
client.publish("rastreador2/estatus", "ONLINE", 0)


## Se envia al HMI los tiempos calculados
control1.publicador(client, "/salida", control1.tiempoDeSalida.strftime("%m/%d/%Y, %H:%M:%S"))
control2.publicador(client, "/salida", control2.tiempoDeSalida.strftime("%m/%d/%Y, %H:%M:%S"))
control3.publicador(client, "/salida", control3.tiempoDeSalida.strftime("%m/%d/%Y, %H:%M:%S"))

#   Definir un atraso 
atrasar_ctl2    =   control2.tiempoDeSalida + datetime.timedelta(seconds=10)


#   acumulador de tiempo
tiempo_de_atraso = 0

#  Definir el estado de los servicios
def runTimer():
    for i in range(len(paneles)):
        if((datetime.datetime.now()   -   paneles[i].tiempo_atraso_cal).total_seconds()   <=  0   and paneles[i].encendido):
            if(paneles[i].atrasado):
                paneles[i].publicador(client, "/estado", "Servicio atrasado")
                paneles[i].publicador(client, "/semaforo", "yellow")
            else:
                paneles[i].publicador(client, "/estado", "A tiempo")
                paneles[i].publicador(client, "/semaforo", "green")
            paneles[i].publicador(client, "/llegada", paneles[i].tiempo_atraso.strftime("%m/%d/%Y, %H:%M:%S"))

        #   Apagado de panel
        elif(
            paneles[i].topic == "control1" or 
            (datetime.datetime.now() >= atrasar_ctl2 and paneles[i].topic == "control2") or 
            (paneles[i].topic == "control3" and (datetime.datetime.now() - paneles[i].tiempo_atraso).total_seconds() <= 0)
            ):
            if(paneles[i].arribo):
                paneles[i].encendido = False
                paneles[i].publicador(client, "/estado", "Apagado")
                paneles[i].publicador(client, "/semaforo", "black")
            if(paneles[i].atrasado):
                if(i + 1 < len(paneles)):
                    tiempo_de_atraso = (datetime.datetime.now()  -   paneles[i].tiempoDeSalida).total_seconds()                 #   delta de servicios en segundos
                    
                    paneles[i + 1].tiempo_atraso += datetime.timedelta(seconds=tiempo_de_atraso)
                    paneles[i + 1].tiempo_atraso_cal   -=  datetime.timedelta(seconds=tiempo_de_atraso) 
                    paneles[i + 1].atrasado = True
                    paneles[i + 1].publicador(client, "/llegada", paneles[i + 1].tiempo_atraso.strftime("%m/%d/%Y, %H:%M:%S"))
                    print(paneles[i + 1].tiempo_atraso)
                paneles[i].atrasado = False

        #   Servicios suprimidos
        elif((datetime.datetime.now()   -   paneles[i].tiempo_atraso_cal).total_seconds()   >  30):
            paneles[i].publicador(client, "/estado", "Servicio suprimido")
            paneles[i].publicador(client, "/semaforo", "red")
            
            tiempo_delta = (datetime.datetime.now()   -   paneles[i].tiempoDeSalida).total_seconds()
            for paneles_encendidos in paneles:
                if(paneles_encendidos.encendido and paneles_encendidos.topic  !=  paneles[i].topic):
                    paneles_encendidos.publicador(client, "/estado", "Servicio suprimido")
                    paneles_encendidos.publicador(client, "/semaforo", "red")
                    paneles_encendidos.publicador(client, "/llegada", "-")
            client.publish("topic/estado", "Termino de recorrido", 0)
            break
            
        else:
           
            #   Servicios atrasados
            paneles[i].publicador(client, "/estado", "Servicio atrasado")
            paneles[i].publicador(client, "/semaforo", "yellow")
            paneles[i].atrasado = True
            
            
            tiempo_delta = (datetime.datetime.now()   -   paneles[i].tiempoDeSalida).total_seconds()
            
            #paneles[i].tiempo_atraso_cal   -=  datetime.timedelta(seconds=tiempo_delta)
            #paneles[i].tiempo_atraso    +=  datetime.timedelta(seconds=tiempo_delta)
            
            if((i + 1) < len(paneles)):
                
                #paneles[i + 1].tiempo_atraso_cal   -=  datetime.timedelta(seconds=tiempo_delta)
                #paneles[i + 1].tiempo_atraso    +=  datetime.timedelta(seconds=tiempo_delta)
                paneles[i + 1].mostrar_calculando(client)
                paneles[i + 1].publicador(client, "/estado", "Servicio atrasado")
                paneles[i + 1].publicador(client, "/semaforo", "yellow")
                #paneles[i + 1].publicador(client, "/llegada", paneles[i + 1].tiempo_atraso.strftime("%m/%d/%Y, %H:%M:%S"))
            paneles[i].publicador(client, "/llegada", datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
            break
inicio = time.time()
client.publish("topic/estado", "Recorrido", 0)
while True:
    runTimer()
    tiempo_actual = time.time()
    duracion = tiempo_actual - inicio
    if duracion >= 64:
        break
    time.sleep(2)

client.publish("topic/estado", "Termino de recorrido", 0)



