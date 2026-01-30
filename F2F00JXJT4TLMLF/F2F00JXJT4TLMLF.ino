#include <Servo.h>

// Definirea obiectelor pentru controlul servomotoarelor
Servo motorOrizontal; // Corespunde axei X
Servo motorVertical;   // Corespunde axei Y

// Definirea pinilor pentru periferice
const int pinLaser = 6;
const int pinLedRosu = 4;
const int pinLedVerde = 5;

// Variabile pentru gestionarea efectului de palpaire (flicker) fara blocarea codului
unsigned long ultimulMomentPalpaire = 0;
bool starePalpaire = false;

void setup() {
  // Initializarea comunicarii seriale la viteza de 115200 baud
  Serial.begin(115200);
  
  // Configurarea pinilor ca iesiri
  pinMode(pinLaser, OUTPUT);
  pinMode(pinLedRosu, OUTPUT);
  pinMode(pinLedVerde, OUTPUT);
  
  // Atasarea servomotoarelor la pinii digitali corespunzatori
  motorOrizontal.attach(9);
  motorVertical.attach(10);
}

void loop() {
  // Verificam daca am primit date noi de la scriptul Python
  if (Serial.available() > 0) {
    // Citim intregul mesaj pana la caracterul de linie noua
    String datePrimite = Serial.readStringUntil('\n');
    
    // Identificam pozitia virgulelor pentru a separa valorile (parsare)
    int v1 = datePrimite.indexOf(',');
    int v2 = datePrimite.indexOf(',', v1 + 1);
    int v3 = datePrimite.indexOf(',', v2 + 1);
    int v4 = datePrimite.indexOf(',', v3 + 1);

    // Validam daca pachetul de date este complet
    if (v1 != -1 && v2 != -1 && v3 != -1 && v4 != -1) {
      // Extragem valorile numerice din sirul de caractere
      int coordX = datePrimite.substring(0, v1).toInt();
      int coordY = datePrimite.substring(v1 + 1, v2).toInt();
      int stareLaser = datePrimite.substring(v2 + 1, v3).toInt();
      int motoareActive = datePrimite.substring(v3 + 1, v4).toInt();
      int tintaBlocata = datePrimite.substring(v4 + 1).toInt();

      // Controlul direct al laserului
      digitalWrite(pinLaser, stareLaser);

      if (motoareActive == 1) {
        // Reactivam servomotoarele daca au fost deconectate
        if (!motorOrizontal.attached()) motorOrizontal.attach(9);
        if (!motorVertical.attached()) motorVertical.attach(10);
        
        // Pozitionam tureta conform coordonatelor primite
        motorOrizontal.write(coordX);
        motorVertical.write(coordY);
        
        // Gestionarea indicatorilor vizuali (LED-uri)
        if (tintaBlocata == 1) {
          digitalWrite(pinLedVerde, LOW); // Stingem LED-ul verde in timpul atacului
          // Efectul de palpaire pentru LED-ul rosu este gestionat mai jos
        } else {
          digitalWrite(pinLedVerde, HIGH); // LED verde aprins in mod urmarire/cautare
          digitalWrite(pinLedRosu, LOW);   // LED rosu stins
        }
      } else {
        // MODUL SOMN (Inactivitate)
        motorOrizontal.write(coordX);
        motorVertical.write(coordY);
        delay(500); // Scurta pauza pentru a ajunge la pozitia de repaus
        
        // Deconectam motoarele pentru a elimina zgomotul si a reduce consumul
        motorOrizontal.detach();
        motorVertical.detach();
        
        // Dezactivam toate perifericele luminoase
        digitalWrite(pinLedVerde, LOW);
        digitalWrite(pinLedRosu, LOW);
        digitalWrite(pinLaser, LOW);
      }
      
      // Actualizam starea palpairii LED-ului rosu
      gestioneazaPalpairea(tintaBlocata, motoareActive);
    }
  }
}

/**
 * Functie pentru crearea efectului de palpaire (mitraliera) a LED-ului rosu.
 * Foloseste functia millis() pentru a nu opri executia restului de cod.
 */
void gestioneazaPalpairea(int blocat, int activ) {
  if (blocat == 1 && activ == 1) {
    // Verificam daca au trecut 80ms de la ultima schimbare de stare
    if (millis() - ultimulMomentPalpaire > 80) { 
      starePalpaire = !starePalpaire; // Inversam starea LED-ului (ON/OFF)
      digitalWrite(pinLedRosu, starePalpaire);
      ultimulMomentPalpaire = millis(); // Resetam cronometrul
    }
  }
}