#include <UTFT.h>
#include <URTouch.h>

UTFT    myGLCD(ILI9341_16,53,52,51,50);
URTouch myTouch(6, 5, 4, 3, 2);

extern unsigned short numpad_up[0x12C00];
extern unsigned short numpad_down[0x12C00];
extern unsigned short numpad_empty_up[0x12C00];
//extern unsigned short load[0x12C00];
extern uint8_t SmallFont[];
extern uint8_t BigFont[];
extern uint8_t SevenSegNumFont[];
int x, y;
int Pagina;
String d_temp = "";
String D;

const int VCC0 = 13;
const int VCC1 = 11;
const int VCC2 = 12;

void setup(){
  //LCD setup
  myGLCD.InitLCD(PORTRAIT);
  myGLCD.clrScr();
  myGLCD.setBrightness(16);

  myTouch.InitTouch(PORTRAIT);
  myTouch.setPrecision(PREC_HI);

  pinMode(VCC0, OUTPUT);
  pinMode(VCC1, OUTPUT);
  pinMode(VCC2, OUTPUT);
  digitalWrite(VCC0, HIGH);
  digitalWrite(VCC1, HIGH);
  digitalWrite(VCC2, HIGH);

  Serial.begin(115200);

  Pagina = '0';
}

void loop(){
  if (Pagina == '0'){
//    myGLCD.drawBitmap(0,0,320,240,load);
    delay(5000);
    Pagina = '1';
    drawNumPad();
  }

  if (myTouch.dataAvailable()) {
    myTouch.read();
    x = myTouch.getX();
    y = myTouch.getY();

    if (d_temp.length() < 6){
      if ((x >= 29) && (x <= 86) && (y >= 70) && (y <= 127)){
        d_temp += "1";
        drawNumPad();
      }
  
      if ((x >= 91) && (x <= 149) && (y >= 70) && (y <= 127)){
        d_temp += "2";
        drawNumPad();
      }
  
      if ((x >= 154) && (x <= 211) && (y >= 70) && (y <= 127)){
        d_temp += "3";
        drawNumPad();
      }
  
      if ((x >= 29) && (x <= 86) && (y >= 133) && (y <=190)){
        d_temp += "4";
        drawNumPad();
      }
  
      if ((x >= 91) && (x <= 149) && (y >= 133) && (y <=190)){
        d_temp += "5";
        drawNumPad();
      }
  
      if ((x >= 154) && (x <= 211) && (y >= 133) && (y <=190)){
        d_temp += "6";
        drawNumPad();
      }
  
      if ((x >= 29) && (x <= 86) && (y >= 195) && (y <= 252)){
        d_temp += "7";
        drawNumPad();
      }
  
      if ((x >= 91) && (x <= 149) && (y >= 195) && (y <= 252)){
        d_temp += "8";
        drawNumPad();
      }
  
      if ((x >= 154) && (x <= 211) && (y >= 195) && (y <= 252)){
        d_temp += "9";
        drawNumPad();
      }
  
      if ((x >= 91) && (x <= 149) && (y >= 258) && (y <= 315) && (d_temp != "")){
        d_temp += "0";
        drawNumPad();
      }
    }

    if ((x >= 29) && (x <= 86) && (y >= 258) && (y <= 315) && (d_temp != "")){
      d_temp.remove(d_temp.length()-1);
      drawNumPad();
    }

    if ((x >= 154) && (x <= 211) && (y >= 258) && (y <= 315) && (d_temp != "")){
      D = d_temp;
      drawConfirmed(D);
    }
  }
}

void drawNumPad() {
  myGLCD.clrScr();
  if (d_temp == ""){
    myGLCD.drawBitmap(0,0,240,160,numpad_empty_up);
    myGLCD.drawBitmap(0,160,240,160,numpad_down);
  }
  else{
    myGLCD.drawBitmap(0,0,240,160,numpad_up);
    myGLCD.drawBitmap(0,160,240,160,numpad_down);
    myGLCD.setColor(255,255,255);
    myGLCD.setFont(SevenSegNumFont);
    myGLCD.print(d_temp,15,12);
  }
}

void drawConfirmed(String D) {
  myGLCD.setColor(VGA_BLACK);
  myGLCD.fillRect(0,110,240,210);
  myGLCD.setFont(BigFont);
  myGLCD.setColor(VGA_WHITE);
  myGLCD.print("Diameter is", CENTER, 120);
  myGLCD.print("confirmed at:", CENTER,140);
  myGLCD.print(D,60,180);
  myGLCD.print("mm",160,180);
  delay(5000);
  drawNumPad();
}
