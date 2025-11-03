#include <stdio.h>
#include <stdlib.h>

#define MAX_FLAG_SIZE 64


__attribute__((constructor)) void ignore_me() {
    setbuf(stdin, NULL);
    setbuf(stdout, NULL);
    setbuf(stderr, NULL);
}
// gcc -static -fno-stack-protector -no-pie oooverflow1.c -o1 -o oooverflow1

int win () {
    system("cat flag.txt");
}

int main() {
    unsigned short key = 0x1234;
    char answer[64];
    
    printf("Tell me, voyager, what is simple, and yet also a riddle: ");
    fgets(answer, 0x64, stdin);
    
    printf("key = 0x%hx\n", key);
    
    if (key == 0x1337) {
        printf("That's it!");
        win();
    } else  {
        printf("That is the wrong answer! The penalty is death by snakes!");
    }
    
    return 0;
}
