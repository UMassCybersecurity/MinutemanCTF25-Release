/*
gcc -m32 -no-pie -Wl,-z,norelro main.c -o charcon
*/

#include<stdio.h>
#include<ctype.h>
#include<stdlib.h>

void win(){
    FILE* flag = fopen("flag.txt", "r");
    if(!flag){
        perror("Opening flag");
        exit(1);
    }
    
    char buffer[256];
    while (fgets(buffer, sizeof(buffer), flag) != NULL) {
        printf("%s", buffer);
    }

    fclose(flag);
}

unsigned int getValue(int hex){
    char buff[2048];
    unsigned int value;

    getchar(); //remove \n

    fgets(buff, sizeof(buff), stdin);

    printf("Converting %s", buff);
    if(hex)
        sscanf(buff, "%x", value);
    else
        sscanf(buff, "%d", &value);
    return value;
}

int main(){
    char cmd;
    unsigned int value;
    
    // Disable buffering for stdout
    setvbuf(stdout, NULL, _IONBF, 0);

    // Disable buffering for stdin
    setvbuf(stdin, NULL, _IONBF, 0);

    while(1){
        printf("Enter number base or quit([D]ecimal/[H]ex/[Q]uit): ");
        cmd = getchar();
        cmd = tolower(cmd);
        
        if(cmd == 'q'){
            puts("goodbye :)");
            return 0;
        }

        if (cmd != 'd' && cmd != 'h'){
            puts("Invalid option! Try again");
            continue;
        }

        printf("Enter nummber to convert in %s: ", cmd == 'd' ? "decimal" : "hex");

        value = getValue(cmd == 'h');

        if(value > 126 || value < 32){
            puts("Unprintable character!");
            continue;
        }

        printf("Your converted character: '%c'\n", value);
    }
}
