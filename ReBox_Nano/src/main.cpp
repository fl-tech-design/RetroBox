#include <Arduino.h>

int buttonsleft[6] = {2, 11, 10, 12, 9, A1};
int buttonsright[6] = {4, 7, 8, A3, A4, A5};

// Vorherige Zustände der Buttons und Potis speichern
int buttonsleft_prev[6] = {HIGH, HIGH, HIGH, HIGH, HIGH, HIGH};
int buttonsright_prev[6] = {HIGH, HIGH, HIGH, HIGH, HIGH, HIGH};

int xSti_1_prev = 0;
int ySti_1_prev = 0;
int xSti_2_prev = 0;
int ySti_2_prev = 0;

int threshold = 300; // Schwellenwert für Poti-Änderungen

int mapPotiValue(int value) {
  // Mappe den Wert von 0-1023 auf -32768 bis 32767
  return map(value, 0, 1023, 32767, -32768);
}

void setup() {
  Serial.begin(9600); // UART starten

  // Pin-Modi für Buttons links und rechts setzen
  for (int i = 0; i < 6; i++) {
    pinMode(buttonsleft[i], INPUT_PULLUP);
    pinMode(buttonsright[i], INPUT_PULLUP);
  }
}

void loop() {
  // Lies und vergleiche die Buttons links
  for (int i = 0; i < 6; i++) {
    int state;

    if (buttonsleft[i] >= A0) {
      // Für analoge Pins, Wert als digitaler Zustand auswerten
      state = analogRead(buttonsleft[i]) > 512 ? HIGH : LOW;
    } else {
      // Für normale digitale Pins
      state = digitalRead(buttonsleft[i]);
    }

    if (state != buttonsleft_prev[i]) { // Nur senden, wenn sich der Zustand ändert
      Serial.print("Button left ");
      Serial.print(i);
      Serial.print(": ");
      Serial.println(state == LOW ? "PRESSED" : "RELEASED"); // Klarere Ausgabe
      buttonsleft_prev[i] = state; // Zustand aktualisieren
    }
  }

  // Lies und vergleiche die Potentiometer
  int xSti_1 = mapPotiValue(analogRead(A0));
  int ySti_1 = mapPotiValue(analogRead(A2));
  int xSti_2 = mapPotiValue(analogRead(A4));
  int ySti_2 = mapPotiValue(analogRead(A5));

  if (abs(xSti_1 - xSti_1_prev) > threshold) {
    Serial.print("X Stick 1: ");
    Serial.println(xSti_1);
    xSti_1_prev = xSti_1;
  }

  if (abs(ySti_1 - ySti_1_prev) > threshold) {
    Serial.print("Y Stick 1: ");
    Serial.println(ySti_1);
    ySti_1_prev = ySti_1;
  }

  if (abs(xSti_2 - xSti_2_prev) > threshold) {
    Serial.print("X Stick 2: ");
    Serial.println(xSti_2);
    xSti_2_prev = xSti_2;
  }

  if (abs(ySti_2 - ySti_2_prev) > threshold) {
    Serial.print("Y Stick 2: ");
    Serial.println(ySti_2);
    ySti_2_prev = ySti_2;
  }

  // Lies und vergleiche die Buttons rechts
  for (int i = 0; i < 6; i++) {
    int state;

    if (buttonsright[i] >= A0) {
      // Für analoge Pins, Wert als digitaler Zustand auswerten
      state = analogRead(buttonsright[i]) > 512 ? HIGH : LOW;
    } else {
      // Für normale digitale Pins
      state = digitalRead(buttonsright[i]);
    }

    if (state != buttonsright_prev[i]) { // Nur senden, wenn sich der Zustand ändert
      Serial.print("Button right ");
      Serial.print(i);
      Serial.print(": ");
      Serial.println(state == LOW ? "PRESSED" : "RELEASED"); // Klarere Ausgabe
      buttonsright_prev[i] = state; // Zustand aktualisieren
    }
  }
}
