import stimulator
import serial
import time
#import bluetooth
import serial.tools.list_ports
import io

a=serial.tools.list_ports.comports()
#print(a)

for w in a:
    print("\tPort:", w.device,"\tSerial#:", w.serial_number, "\tDesc:", w.description)
    if w.description == 'USB2.0-Serial':
        bd_addr = w.device
    elif w.description == 'USB <-> Stimu_Control':
        stimulatorPort = w.device
'''        
print('porta controle:', bd_addr)
print('porta stimulador:', stimulatorPort)

ser = serial.Serial()
ser.port = bd_addr
ser.timeout = 1
ser.bourate = 115200
ser.xonxoff = 1

print('esperando 5 seg antes de abrir')
time.sleep(5);

try:
    ser.open()
    print('depois 5 seg antes de abrir')
    time.sleep(5);
    
    print('Porta aberta')
except Exeption as erro:
    print('Error em: ' + str(erro))
    
print('Continuando porta aberta')

start_receiver = True
msg = '123'


if ser.isOpen():
    try:
        print(msg)
        msg_bytes = str.encode(msg)
        print('esperando 5 seg')
        time.sleep(5);
        print('terminou esperando 5 seg')
        ser.write(msg_bytes)
        
            
        while start_receiver is True:
            c = ser.readline()
            if len(c) > 0:
                str_msn = c.decode()
                str_msn = str_msn.rstrip()
                print(str_msn)
                if str_msn == 'conectou':
                    print("Puede mandar un nuevo comando")
                    start_receiver = False

    except Exception as e1:
        print('Error communicating...: ' + str(e1))
        
else:
    print("Cannot open serial port " + str(port) + "En -- puerta no abierta --")
    exit()
    
'''
   
sock = serial.Serial(bd_addr, baudrate=9600, timeout=0.1)
time.sleep(15)

running = True
stimulation = True

print("Conectando")

statSend = True
statWait = True

sock.write(b'a') # envia 'a' sinalizando a conexao para o controlador
#while statSend == True:
time.sleep(1)
temp= sock.readline()
Temp = temp.decode()
Temp = temp[0:8]
if temp == 'conectou':
    statWait = False
    statSend = False     

print("Conectado")

statWait = True
while statWait == True:
    parametros = sock.readline().decode()
    parametros = parametros[0:20]
    if parametros != '':
        statWait = False
        
serialStimulator = serial.Serial(stimulatorPort, baudrate=115200, timeout=0.1)
stim = stimulator.Stimulator(serialStimulator) #chama a classe
time.sleep(5)


print('recebeu parametros:')
print(parametros)

flag = parametros

   
def stim_setup():
    print(flag)
    current_A = int(flag[1:4])
    current_B = int(flag[5:8])
    pw = int(flag[9:12])
    freq = int(flag[13:16])
    mode = int(flag[17:20])
    print(current_A,current_B,pw,mode,freq)
    canais = channels(mode)
    
    # Os parametros sao frequencias e canais
    stim.initialization(freq,canais)

    return [current_A,current_B,pw,mode,canais]

# mode eh a quantidade de canais utilizados e channels e como a funcao stim.inicialization interpreta esse canais
# logo, eh necessario codificar a quantidade de canais nessa forma binaria ,o mais a esquerda eh o 8 e o mais a direita eh o 1
def channels(mode):
    if mode == 2:
        channels = 0b00000011
    elif mode == 4:
        channels = 0b00001111
    elif mode == 6:
        channels = 0b00111111
    elif mode == 8:
        channels = 0b11111111

    return channels

def running(current_A,current_B,pw,mode,channels):
    
    #cria um vetor com as correntes para ser usado pela funcao update
    current_str = []
    if mode == 2:
        current_str.append(current_A)
        current_str.append(current_A)
    elif mode == 4: # Canais 1 e 2 terao corrente A e canais 3 e 4 corrent B
        current_str.append(current_A)
        current_str.append(current_A)
        current_str.append(current_B)
        current_str.append(current_B)
        
    sock.write(b'a') # envia 'a' sinalizando a conexao para o controlador
    print("running")
    
    
    state = 0
    print(state)
    while state != 3:
        while sock.inWaiting() == 0:
            pass
        state = int(sock.read(1))#state = int(sock.read(1))
        print(state)
        if mode == 2:                           # Para 2 canais
            if state == 0: 
                print("Parado")
                stim.update(channels,[0,0], current_str)
               # stim.stop()
            elif state == 1:
                stim.update(channels, [pw,pw], current_str)    
                print("Extensao")       
            elif state == 2:
                stim.update(channels, [0,0], current_str)    
                print("Contracao")    
        elif mode == 4:                         # Para 4 canais
            if state == 0: 
                print("Parado")
                stim.update(channels,[0,0,0,0], current_str)
               # stim.stop()
            elif state == 1:
                stim.update(channels,[0,0,pw,pw], current_str)    
                print("Extensao")       
            elif state == 2:
                stim.update(channels,[pw,pw,0,0], current_str)    
                print("Contracao")    
            #para usar 6 ou 8 canais eh necessario copiar o codigo logo acima e mudar somente o vetor pw,
            #colocando-se pw no canal que se quer estimular
    
def main():
    [current_A,current_B,pw,mode,channels] = stim_setup()
    print(current_A,current_B,pw,mode,channels)
    running(current_A,current_B,pw,mode,channels)

    stim.stop()
    sock.close()
    serialStimulator.close()
    print("Saiu")

if __name__ == '__main__':
    main()



    


    