#include "cpu/br25/uart.h"

#define FLAG "\x1d\x19\x1e\x05\x04\x15\x1d\x11\x1e+3\x021*\t\x0f9>#\x04\"%3\x049?>#-"
#define UART_TX "PA05"


int main(){
    char data[sizeof(FLAG)] = FLAG;
    for(int i = 0; i < sizeof(FLAG); i++){
        data[i] ^= 0x50;
    }

    uart_init(UART_TX, 115200);

    for(int j = 0; j < sizeof(FLAG); j++){
        putchar(data[j]);
    }

    uart_close();
}