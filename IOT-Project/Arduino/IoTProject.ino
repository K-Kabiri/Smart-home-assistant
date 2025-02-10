#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "ESP32_AP";  
const char* password = "12345678";  

WebServer server(80);
#define KitchenLED 4 
#define RoomLED 12 
#define ParkingLED 13

const char* formHTML = R"rawliteral( 
<!DOCTYPE html> 
<html> 
<head> 
  <title>ESP32 LED Control</title> 
  <style> 
    body { 
      font-family: Arial, sans-serif; 
      background: url('https://png.pngtree.com/thumb_back/fh260/background/20230707/pngtree-d-rendering-of-iot-devices-and-network-connection-in-the-internet-image_3766498.jpg')) no-repeat center center fixed; 
      background-size: cover; 
      color: white; 
      text-align: center; 
      padding: 50px 0; 
    } 
    h2 { 
      font-size: 2em; 
      margin-bottom: 20px; 
    } 
    form { 
      background-color: rgba(0, 0, 0, 0.6); 
      padding: 30px; 
      border-radius: 10px; 
      display: inline-block; 
    } 
    label { 
      font-size: 1.2em; 
      margin-bottom: 10px; 
    } 
    input[type='text'] { 
      padding: 10px; 
      font-size: 1.2em; 
      width: 300px; 
      margin-bottom: 20px; 
      border: none; 
      border-radius: 5px; 
      background-color: #f0f0f0; 
    } 
    input[type='submit'] { 
      padding: 12px 30px; 
      font-size: 1.2em; 
      background-color: #4CAF50; 
      color: white; 
      border: none; 
      border-radius: 5px; 
      cursor: pointer; 
    } 
    input[type='submit']:hover { 
      background-color: #45a049; 
    } 
  </style> 
</head> 
<body> 
  <h2>ESP32 Data Form</h2> 
  <form action="/submit" method="post"> 
    <label for="data">Enter data:</label><br><br> 
    <input type="text" id="data" name="data" required><br><br> 
    <input type="submit" value="Submit"> 
  </form> 
</body> 
</html> 
)rawliteral";

void handleRoot() {
  server.send(200, "text/html", formHTML);
}

void handleSubmit() {
  if (server.method() == HTTP_POST) {
    if (server.hasArg("data")) {
      String data = server.arg("data");

      Serial.println(data);

      server.send(200, "text/html", "<h2>Data received: " + data + "</h2><a href='/'>Go back</a>");
    } else {
      server.send(400, "text/plain", "Bad Request: Missing 'data'");
    }
  } else {
    server.send(405, "text/plain", "Method Not Allowed");
  }
}

void blinkLED(int delayTime, int times) {
  for (int i = 0; i < times; i++) {
    digitalWrite(KitchenLED, HIGH);
    delay(delayTime);
    digitalWrite(KitchenLED, LOW);
    delay(delayTime);
  }
}

void setup() {
  Serial.begin(115200); 
  pinMode(KitchenLED, OUTPUT);  
  pinMode(RoomLED, OUTPUT);  
  pinMode(ParkingLED, OUTPUT);  

  digitalWrite(KitchenLED, LOW);
  digitalWrite(RoomLED, LOW);
  digitalWrite(ParkingLED, LOW);


  WiFi.softAP(ssid, password);
  Serial.println("Access Point started");
  Serial.print("IP address: ");
  Serial.println(WiFi.softAPIP());

  server.on("/", handleRoot);
  server.on("/submit", handleSubmit);

  server.begin();
  Serial.println("Web server started");
}

void loop() {
  server.handleClient();  
 
  if (Serial.available()) {  
    String data = Serial.readString();  
      
    for (int i = 0; i < data.length(); i++) { 
      char response = data.charAt(i);  
 
      if (response == 'A') {  
        digitalWrite(KitchenLED, HIGH); 
        Serial.println("Kitchen LED turned ON."); 
      }  
      else if (response == 'B') {  
        digitalWrite(KitchenLED, LOW);   
        Serial.println("Kitchen LED turned OFF."); 
      }  
      else if (response == 'C') {  
        digitalWrite(RoomLED, HIGH);  
        Serial.println("Room LED turned ON."); 
      }  
      else if (response == 'D') {  
        digitalWrite(RoomLED, LOW);  
        Serial.println("Room LED turned OFF."); 
      }  
      else if (response == 'E') {  
        digitalWrite(ParkingLED, HIGH);  
        Serial.println("Parking LED turned ON."); 
      }  
      else if (response == 'F') {  
        digitalWrite(ParkingLED, LOW);  
        Serial.println("Parking LED turned OFF."); 
      }  
      else { 
        Serial.println("⚠️ Invalid command received."); 
      } 
    } 
}
}
