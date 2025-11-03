#include <stdio.h>
#include <string.h>

void print_flag()
{
    unsigned char encoded[] = {0x6c, 0x51, 0x49, 0x5a, 0x47, 0x4c, 0x4b, 0x58, 0x58};
    int len = 9;

    for (int i = 0; i < len; i++)
    {
        putchar(encoded[i] ^ 0x3e);
    }
}

int main()
{
    char input[100];
    printf("Enter the secret: ");
    fgets(input, sizeof(input), stdin);
    input[strcspn(input, "\n")] = 0;

    if (strcmp(input, "salt") == 0)
    {
        printf("MINUTEMAN{");
        print_flag();
        printf("}\n");
    }
    else
    {
        printf("Wrong!\n");
    }

    return 0;
}