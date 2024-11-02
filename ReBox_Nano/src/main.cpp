#include <Arduino.h>

// RGB-LED Pins
const int led1Pins[3] = {3, 6, 11}; // Rot, Grün, Blau Pins für LED 1
const int led2Pins[3] = {5, 9, 10}; // Rot, Grün, Blau Pins für LED 2

// Fade Einstellungen
int brightness[3] = {0, 0, 0};    // Helligkeitswerte für R, G, B
int fadeAmount = 5;               // Schrittgröße für das Fading
unsigned long previousMillis = 0; // Speichert die Zeit des letzten Updates
const long interval = 90;         // Zeitintervall für das Fading
int currentColor = 0;             // Aktuelle Farbe (0 = Rot, 1 = Grün, 2 = Blau)

// Ventilation
const int venti_pin = 8;

// Serial Data Transfer
unsigned long lastSendTime = 0;        // Zeitstempel für letzte Übertragung
const unsigned long sendInterval = 30; // Intervall in Millisekunden
int serialData[4] = {0, 0, 0, 0};      // Array für Datenübertragung: Joystick-Werte und Ventilationsstatus

void rgbDemo()
{
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval)
  {
    previousMillis = currentMillis;

    // Helligkeit für die aktuelle Farbe anpassen
    brightness[currentColor] += fadeAmount;

    // Wenn die Helligkeit den Grenzwert erreicht, Richtung umkehren
    if (brightness[currentColor] <= 0 || brightness[currentColor] >= 255)
    {
      fadeAmount = -fadeAmount;

      // Wenn die Farbe zurück auf 0 gedimmt wurde, zur nächsten Farbe wechseln
      if (brightness[currentColor] <= 0)
      {
        currentColor = (currentColor + 1) % 3; // Zyklus Rot -> Grün -> Blau
      }
    }

    // Helligkeit nur für die aktuelle Farbe anwenden, andere Farben ausschalten
    for (int i = 0; i < 3; i++)
    {
      analogWrite(led1Pins[i], (i == currentColor) ? brightness[i] : 0);
      analogWrite(led2Pins[i], (i == currentColor) ? brightness[i] : 0);
    }
  }
}

void setRgbColor(int r, int g, int b)
{
  for (int i = 0; i < 3; i++)
  {
    analogWrite(led1Pins[i], i == 0 ? r : (i == 1 ? g : b));
    analogWrite(led2Pins[i], i == 0 ? r : (i == 1 ? g : b));
  }
}
// Analog-Stick-Werte lesen und zentrieren
int readCenteredAnalog(int pin)
{
  int rawValue = analogRead(pin);

  // Falls Wert in Toleranzbereich liegt, auf 512 setzen
  if (rawValue >= 460 && rawValue <= 580)
  {
    return 512;
  }

  // Wertebereich spiegeln (umkehren) bei Bedarf
  return rawValue;
}

void readAnalogStick()
{
  // Joystick-Daten lesen und speichern
  serialData[0] = 1023 - readCenteredAnalog(A2); // X-Achse
  serialData[1] = 1023 - readCenteredAnalog(A3); // Y-Achse
  serialData[2] = readCenteredAnalog(A1);        // Zweiter Stick X-Achse (falls benötigt)
  serialData[3] = readCenteredAnalog(A0);        // Zweiter Stick Y-Achse (falls benötigt)
}
void readSerialData() {
  if (Serial.available() > 0) {
    int receivedValue = Serial.parseInt(); // Liest eine Ganzzahl
    if (receivedValue == 0 || receivedValue == 1) { // Nur 0 oder 1 akzeptieren
      digitalWrite(venti_pin, receivedValue);
    }
    Serial.flush();  // Optional: Puffer leeren, falls es mehrere Werte gibt
  }
}

void sendSerialData()
{
  unsigned long currentTime = millis();

  // Prüfen, ob das Intervall erreicht ist
  if (currentTime - lastSendTime >= sendInterval)
  {
    lastSendTime = currentTime; // Zeitstempel aktualisieren

    // Alle Elemente von serialData senden, getrennt durch Komma
    for (int i = 0; i < 4; i++)
    {
      Serial.print(serialData[i]);
      if (i < 3)
        Serial.print(","); // Trennzeichen hinzufügen, außer beim letzten Element
    }
    Serial.println(); // Neue Zeile für nächsten Datensatz
  }
}

void setup()
{
  Serial.begin(9600);
  for (int i = 0; i < 3; i++)
  {
    pinMode(led1Pins[i], OUTPUT);
    pinMode(led2Pins[i], OUTPUT);
  }
  pinMode(venti_pin, OUTPUT);
}

void loop()
{
  rgbDemo(); // Falls RGB-Demo benötigt wird
  readAnalogStick();
  sendSerialData();
  readSerialData();
}
