import cv2
from cvzone.FaceDetectionModule import FaceDetector
import numpy as np
import time
import serial
import pygame
import os

# ---------------- CONFIGURĂRI ȘI INTERFAȚĂ ----------------
latime_fereastra, inaltime_fereastra = 1280, 720
# Definire interval culori pentru detectarea punctului laser (HSV)
rosu_jos = np.array([0, 100, 245]) 
rosu_sus = np.array([180, 255, 255])

INVERSARE_X, INVERSARE_Y = -1, -1
VITEZA_URMARIRE = 0.15 
VITEZA_CAUTARE = 0.8 
TIMP_ASTEPTARE_SOMN = 15  
COORD_SOMN_X, COORD_SOMN_Y = 90, 160  

def nimic(x): pass

# Creare fereastră pentru calibrare parametri
cv2.namedWindow("Calibrare")
cv2.createTrackbar("Kp", "Calibrare", 15, 100, nimic) 
cv2.createTrackbar("Ki", "Calibrare", 0, 100, nimic) 
cv2.createTrackbar("Kd", "Calibrare", 5, 100, nimic)
cv2.createTrackbar("Ajustare_X", "Calibrare", 100, 200, nimic) 
cv2.createTrackbar("Ajustare_Y", "Calibrare", 100, 200, nimic)
cv2.createTrackbar("Zona_Lock", "Calibrare", 80, 200, nimic)
cv2.createTrackbar("Manual_X", "Calibrare", 90, 180, nimic)
cv2.createTrackbar("Manual_Y", "Calibrare", 120, 180, nimic)

# ---------------- CONFIGURARE AUDIO ----------------
pygame.mixer.init()
pygame.mixer.set_num_channels(8)
CALE_SUNETE = "portal sounds/"

# Inițializare obiecte sunet
sunet_tinta_gasita = None
sunet_tinta_pierduta = None
sunet_voce_foc = None
sunet_mitraliera_loop = None
sunet_somn = None
sunet_asteptare = None

try:
    sunet_tinta_gasita = pygame.mixer.Sound(CALE_SUNETE + "0011-target acquired.mp3")
    sunet_tinta_pierduta = pygame.mixer.Sound(CALE_SUNETE + "0007-target lost.mp3")
    sunet_voce_foc = pygame.mixer.Sound(CALE_SUNETE + "0070 - Firing.mp3") 
    sunet_mitraliera_loop = pygame.mixer.Sound(CALE_SUNETE + "0015-fire.mp3")
    sunet_somn = pygame.mixer.Sound(CALE_SUNETE + "0014-Turret_die.mp3")
    sunet_asteptare = pygame.mixer.Sound(CALE_SUNETE + "0006-are you still there.mp3")
    print("Sistemul audio a fost incarcat cu succes!")
except Exception as e:
    print(f"!!! Eroare la incarcarea sunetelor: {e}")

def reda_sunet(obiect_sunet):
    if obiect_sunet: obiect_sunet.play()

# ---------------- CONFIGURARE HARDWARE (ARDUINO) ----------------
try:
    # Conexiune seriala cu Arduino pe portul COM8
    conexiune_seriala = serial.Serial('COM8', 115200, timeout=0.1)
    time.sleep(2)
except:
    print("Eroare Seriala! Verifica portul COM."); exit()

# Initializare camera si detector facial
camera = cv2.VideoCapture(0)
camera.set(3, latime_fereastra); camera.set(4, inaltime_fereastra)
detector_fata = FaceDetector()

# Variabile stare sistem
x_curent, y_curent = 90.0, 120.0
ultima_trimitere_x, ultima_trimitere_y = -1, -1
ultima_stare_servo = -1
ultima_stare_blocare = -1
ultima_stare_laser = -1
eroare_prev_x, eroare_prev_y = 0, 0
integrala_x, integrala_y = 0, 0
timp_precedent = time.time()
regim_lucru = "AUTO"
pas_cautare = 0
moment_blocare_tinta = 0
moment_start_inactivitate = time.time()
voce_redata = False
sunet_somn_redat = False 
stare_precedenta = "IDLE"

while True:
    delta_t = max(time.time() - timp_precedent, 0.01)
    timp_precedent = time.time()

    succes, cadru = camera.read()
    if not succes: break
    
    # Detectare punct laser prin masca de culoare
    hsv = cv2.cvtColor(cadru, cv2.COLOR_BGR2HSV)
    masca_laser = cv2.inRange(hsv, rosu_jos, rosu_sus)
    momente = cv2.moments(masca_laser)
    coord_laser_x, coord_laser_y = -1, -1
    if momente["m00"] > 30:
        coord_laser_x = int(momente["m10"] / momente["m00"])
        coord_laser_y = int(momente["m01"] / momente["m00"])
        cv2.circle(cadru, (coord_laser_x, coord_laser_y), 10, (0, 255, 255), 2)

    # Detectare fete umane
    cadru, fete_detectate = detector_fata.findFaces(cadru, draw=False)

    # Preluare valori din trackbar-uri pentru algoritmul PID
    kp = cv2.getTrackbarPos("Kp", "Calibrare") / 2000.0 
    ki = cv2.getTrackbarPos("Ki", "Calibrare") / 10000.0 
    kd = cv2.getTrackbarPos("Kd", "Calibrare") / 2000.0
    ajust_x = (cv2.getTrackbarPos("Ajustare_X", "Calibrare") - 100) * 5
    ajust_y = (cv2.getTrackbarPos("Ajustare_Y", "Calibrare") - 100) * 5
    prag_blocare = max(cv2.getTrackbarPos("Zona_Lock", "Calibrare"), 10)
    manual_x = cv2.getTrackbarPos("Manual_X", "Calibrare")
    manual_y = cv2.getTrackbarPos("Manual_Y", "Calibrare")

    stare_laser = 1 
    servo_activ = 1 
    tinta_blocata_arduino = 0
    eroare_x = eroare_y = 0

    if regim_lucru == "AUTO":
        if fete_detectate:
            moment_start_inactivitate = time.time()
            sunet_somn_redat = False 
            servo_activ = 1
            centru_x, centru_y = fete_detectate[0]["center"]
            tinta_x, tinta_y = centru_x + ajust_x, centru_y + ajust_y
            
            cv2.circle(cadru, (int(tinta_x), int(tinta_y)), prag_blocare, (0, 255, 0), 1)

            if coord_laser_x != -1:
                # Calculare eroare intre tinta dorita si punctul laser actual
                eroare_x, eroare_y = tinta_x - coord_laser_x, tinta_y - coord_laser_y
                distanta = np.sqrt(eroare_x**2 + eroare_y**2)
                
                if distanta < prag_blocare:
                    mesaj_stare = "LOCKED"
                    culoare_cursor = (0, 0, 255)
                    tinta_blocata_arduino = 1 
                else:
                    mesaj_stare = "TRACKING"
                    culoare_cursor = (0, 255, 0)
                    tinta_blocata_arduino = 0 

                cv2.drawMarker(cadru, (int(tinta_x), int(tinta_y)), culoare_cursor, cv2.MARKER_CROSS, 20, 2)

                if stare_precedenta not in ["LOCKED", "TRACKING"]:
                    moment_blocare_tinta = time.time()
                    voce_redata = False
                    reda_sunet(sunet_tinta_gasita)

                # Implementare calcul PID
                integrala_x = np.clip(integrala_x + (eroare_x * delta_t), -10, 10)
                integrala_y = np.clip(integrala_y + (eroare_y * delta_t), -10, 10)
                derivata_x = (eroare_x - eroare_prev_x) / delta_t
                derivata_y = (eroare_y - eroare_prev_y) / delta_t
                
                x_curent += ((eroare_x * kp) + (integrala_x * ki) + (derivata_x * kd)) * INVERSARE_X * VITEZA_URMARIRE
                y_curent += ((eroare_y * kp) + (integrala_y * ki) + (derivata_y * kd)) * INVERSARE_Y * VITEZA_URMARIRE
                eroare_prev_x, eroare_prev_y = eroare_x, eroare_y
                pas_cautare = 0

                # Logica pentru secventa de tragere
                if mesaj_stare == "LOCKED":
                    timp_de_la_blocare = time.time() - moment_blocare_tinta
                    if timp_de_la_blocare > 1.5 and not voce_redata:
                        reda_sunet(sunet_voce_foc)
                        voce_redata = True
                    if timp_de_la_blocare > 2.0 and sunet_mitraliera_loop:
                        if not pygame.mixer.Channel(2).get_busy():
                            pygame.mixer.Channel(2).play(sunet_mitraliera_loop, loops=-1)
                else:
                    pygame.mixer.Channel(2).stop()
            else:
                # Mod recuperare: cautare punct laser in jurul tintei
                mesaj_stare = f"SEARCHING: {pas_cautare}"
                cv2.drawMarker(cadru, (int(tinta_x), int(tinta_y)), (0, 255, 0), cv2.MARKER_CROSS, 20, 2)
                if stare_precedenta in ["LOCKED", "TRACKING"]:
                    reda_sunet(sunet_tinta_pierduta)
                    pygame.mixer.Channel(2).stop()
                
                if pas_cautare == 0:
                    y_curent -= VITEZA_CAUTARE
                    if y_curent <= 100: pas_cautare = 1
                elif pas_cautare == 1:
                    x_curent += VITEZA_CAUTARE
                    if x_curent >= 160: pas_cautare = 2
                elif pas_cautare == 2:
                    y_curent += VITEZA_CAUTARE
                    if y_curent >= 160: pas_cautare = 3
                elif pas_cautare == 3:
                    x_curent -= VITEZA_CAUTARE
                    if x_curent <= 20: pas_cautare = 0
        else:
            # Sistem inactiv: nicio fata detectata
            pygame.mixer.Channel(2).stop()
            if time.time() - moment_start_inactivitate > TIMP_ASTEPTARE_SOMN:
                mesaj_stare = "SLEEP MODE"
                x_curent, y_curent = COORD_SOMN_X, COORD_SOMN_Y
                servo_activ = 0 
                stare_laser = 0 
                if not sunet_somn_redat:
                    reda_sunet(sunet_somn)
                    sunet_somn_redat = True
            else:
                mesaj_stare = "IDLE - CAUTARE FATA"
                if not voce_redata and time.time() - moment_start_inactivitate > TIMP_ASTEPTARE_SOMN / 2:
                    reda_sunet(sunet_asteptare)
                    voce_redata = True
                servo_activ = 1
                stare_laser = 1
    else:
        # Control manual prin trackbar-uri
        mesaj_stare = "CONTROL MANUAL"
        x_curent, y_curent = float(manual_x), float(manual_y)
        stare_laser = 1
        servo_activ = 1
        tinta_blocata_arduino = 0
        pygame.mixer.Channel(2).stop()

    stare_precedenta = mesaj_stare
    x_curent, y_curent = np.clip(x_curent, 20, 200), np.clip(y_curent, 100, 160)
    
    # Transmitere date catre Arduino doar la schimbarea valorilor
    if (int(x_curent) != ultima_trimitere_x or int(y_curent) != ultima_trimitere_y or 
        servo_activ != ultima_stare_servo or tinta_blocata_arduino != ultima_stare_blocare or
        stare_laser != ultima_stare_laser):
        
        comanda = f"{int(x_curent)},{int(y_curent)},{stare_laser},{servo_activ},{tinta_blocata_arduino}\n"
        conexiune_seriala.write(comanda.encode())
        
        ultima_trimitere_x, ultima_trimitere_y = int(x_curent), int(y_curent)
        ultima_stare_servo = servo_activ
        ultima_stare_blocare = tinta_blocata_arduino
        ultima_stare_laser = stare_laser

    # Desenare interfata utilizator (Overlay)
    cv2.rectangle(cadru, (20, 20), (450, 190), (0,0,0), -1) # Am marit putin dreptunghiul
    cv2.putText(cadru, f"MOD: {mesaj_stare}", (30, 50), 1, 1.5, (0, 255, 255), 2)
    cv2.putText(cadru, f"SERVO: {int(x_curent)}, {int(y_curent)} {'(OFF)' if not servo_activ else ''}", (30, 80), 1, 1.5, (255, 255, 255), 2)
    
    # Afisare eroare PID (diferenta dintre laser si tinta)
    # Daca laserul nu e detectat, afisam "N/A"
    txt_eroare = f"EROARE: X:{int(eroare_x)} Y:{int(eroare_y)}" if coord_laser_x != -1 else "EROARE: Laser nedetectat"
    cv2.putText(cadru, txt_eroare, (30, 110), 1, 1.5, (0, 200, 255), 2)
    
    # Optional: Afisare distanta totala (euclidiana) pana la tinta
    if coord_laser_x != -1:
        distanta_totala = int(np.sqrt(eroare_x**2 + eroare_y**2))
        cv2.putText(cadru, f"DIST. TINTA: {distanta_totala} px", (30, 140), 1, 1.2, (100, 255, 100), 2)

    cv2.imshow("Sistem Urmarire Tureta", cadru)
    tasta = cv2.waitKey(1) & 0xFF
    if tasta == ord('q'): break # Iesire program
    elif tasta == ord('m'): regim_lucru = "MANUAL"
    elif tasta == ord('a'): regim_lucru = "AUTO"

camera.release()
cv2.destroyAllWindows()