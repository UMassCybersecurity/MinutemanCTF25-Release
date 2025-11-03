#include <stdio.h>

#define MAX_FLAG_SIZE 72

__attribute__((constructor)) void ignore_me() {
    setbuf(stdin, NULL);
    setbuf(stdout, NULL);
    setbuf(stderr, NULL);
}

// gcc -static -fno-stack-protector -no-pie vuln.c -o vuln
void winner (int a, int b) {
    if (a != 0xCAFEBABE || b != 0xDEADBEEF) {
        return;
    }
    
    FILE *fp = fopen("flag.txt", "r");

    if (fp == NULL) {
        printf("Flag not found!\n");
    }

    char flag[MAX_FLAG_SIZE];

    fscanf(fp, "%71s", flag);

    printf("\nCongrats!\n\n%s\n", flag);

    fclose(fp);
}

int main() {
    
    char buf[32];
    printf("My name is Key-per, and duly so, for I carry the key to this door, \nbut all is not how it appears, you see.");
    printf("\nOr perhaps you do not see at all. ");
    printf("\nPerhaps the key is in you, child, but you cannot use your brawn here. \nThe door is magically sealed.\n");
    printf("\nEnter your response challenger: ");
    
    fgets(buf, 0x60, stdin);

    return 0;
}