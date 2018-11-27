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
    if mode == 0:
        channels = 0b00000000  # Estado Inicial
    elif mode == 1:
        channels = 0b00000011  # Extensão
    elif mode == 2:
        channels = 0b00001100  # Flexão
    elif mode == 3:
        channels = 0b00001111  # Extensão + Flexão
    elif mode == 4:
        channels = 0b00110011  # (Extensão & Aux_Ext)
    elif mode == 5:
        channels = 0b00111111  # (Extensão & Aux_Ext) + Flexão
    elif mode == 6:
        channels = 0b11001100  # (Flexão & Aux_Flex)
    elif mode == 7:
        channels = 0b11001111  # Extensao + (Flexão & Aux_Flex)
    elif mode == 8:
        channels = 0b11111111  # (Extensão & Aux_Ext) + (Flexão & Aux_Flex)

    return channels

def running(current_A,current_B,pw,mode,channels):
    
    #cria um vetor com as correntes para ser usado pela funcao update
    current_str = []
    if mode == 1:
        current_str.append(current_A)
        current_str.append(current_A)
    elif mode == 3: # Canais 1 e 2 terao corrente A e canais 3 e 4 corrent B
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