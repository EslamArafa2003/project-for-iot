#include <Arduino.h>
#include <WiFi.h>
#include <FirebaseESP32.h>
#define LED_BUILTIN 2
#include <addons/TokenHelper.h>
#include <addons/RTDBHelper.h>
#include <Preferences.h>

#define ECHO_PIN 17
#define TRIG_PIN 16

Preferences preferences;
const char* wifiSSIDs[] = {"tedata"};
const char* wifiPasswords[] = {"19851985"};
int numberOfNetworks = sizeof(wifiSSIDs);
int currentNetworkIndex = 0;

#define API_KEY "AIzaSyD2v8i1VOnY1Hd4sIXmPUXiKGgRQFfK9NA"
#define DATABASE_URL "https://task1-a7033-default-rtdb.firebaseio.com/"
#define USER_EMAIL "arafaeslam2003@gmail.com"
#define USER_PASSWORD "Eslam@2003"

FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

unsigned long sendDataPrevMillis = 0;
unsigned long counter;

void connectToWiFi() {
  Serial.println("Connecting to WiFi...");
  bool connected = false;
  for (int i = 0; i < numberOfNetworks; i++) {
    WiFi.begin(wifiSSIDs[currentNetworkIndex], wifiPasswords[currentNetworkIndex]);
    Serial.print("Attempting to connect to ");
    Serial.print(wifiSSIDs[currentNetworkIndex]);
    Serial.println("...");
    int attempts = 10;
    while (WiFi.status() != WL_CONNECTED && attempts > 0) {
      delay(1000);
      Serial.print(".");
      attempts--;
    }
    if (WiFi.status() == WL_CONNECTED) {
      connected = true;
      Serial.println("\nWiFi connected.");
      Serial.print("IP address: ");
      Serial.println(WiFi.localIP());
      break;
    } else {
      Serial.println("\nConnection failed.");
      currentNetworkIndex = (currentNetworkIndex + 1) % numberOfNetworks;
    }
  }

  if (!connected) {
    Serial.println("Failed to connect to WiFi. Please check your credentials");
    connectToWiFi();
  }
}

void setup()
{
  Serial.begin(115200);
  connectToWiFi();
  pinMode(LED_BUILTIN,OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(TRIG_PIN, OUTPUT);

  Serial.printf("Firebase Client v%s\n\n", FIREBASE_CLIENT_VERSION);
  preferences.begin("my-app",false);
  unsigned long count= preferences.getUInt("count",0);
  counter=count;
  Serial.print("Counter will start from :");
  Serial.print(count);
  Serial.print("\n...");

  config.api_key = API_KEY;
  auth.user.email = USER_EMAIL;
  auth.user.password = USER_PASSWORD;
  config.database_url = DATABASE_URL;
  config.token_status_callback = tokenStatusCallback;

  Firebase.reconnectNetwork(true);
  fbdo.setBSSLBufferSize(4096, 1024);
  Firebase.begin(&config, &auth);
  Firebase.setDoubleDigits(5);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi connection lost. Reconnecting...");
    connectToWiFi();
  }
  if (Firebase.ready() && (millis() - sendDataPrevMillis > 15000 || sendDataPrevMillis == 0)) {
    sendDataPrevMillis = millis();

    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);

    long duration = pulseIn(ECHO_PIN, HIGH);
    long distance = (duration/2) / 29.1;

    FirebaseJson json;
    Serial.println(counter);
    String path = "/readings/" + String(counter);
    Serial.println("CURRENT dir is ......");
    Serial.println(path);
    json.set("value", distance);
    json.set("timestamp/.sv", "timestamp");

    if (Firebase.set(fbdo, path, json)) {
      Serial.println("Reading and timestamp sent successfully.");
      digitalWrite(LED_BUILTIN,HIGH);
      preferences.putUInt("count",counter);
    } else {
      Serial.println("Failed to send reading and timestamp: " + fbdo.errorReason());
    }
    counter++;
    delay(1000);
    digitalWrite(LED_BUILTIN,LOW);
  }
}