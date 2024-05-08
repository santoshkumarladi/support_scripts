#include <unistd.h>
#include <sys/file.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdlib.h>
#include <pthread.h>
#include <stdio.h>
#include <string.h>

int fd;
off_t read_offset;
int q = 0;


char* readable_fs(double size/*in bytes*/, char *buf) {
    int i = 0;
    const char* units[] = {"B", "kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"};
    while (size > 1024) {
        size /= 1024;
        i++;
    }
    sprintf(buf, "%.*f %s", i, size, units[i]);
    return buf;
}

static char *rand_string(char *str, size_t size)
{
    //const char charset[] = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJK...";
    const char charset[] = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,.-#'?!";
    if (size) {
        --size;
        for (size_t n = 0; n < size; n++) {
            int key = rand() % (int) (sizeof charset - 1);
            str[n] = charset[key];
        }
        str[size] = '\0';
    }
    return str;
}

void* reader_routine(void* p)
{
    char buffer[32] = {0};
    int bytesRead = 0;

    while(!q)
    {
        flock(fd, LOCK_EX);
        lseek(fd, read_offset, SEEK_SET);
        bytesRead = read(fd, buffer, 32);
        flock(fd, LOCK_UN);
        if (bytesRead > 0)
        {
            read_offset = lseek(fd, read_offset + bytesRead, SEEK_SET);
            buffer[bytesRead] = 0;
            puts(buffer);
        }
    }

    lseek(fd, read_offset, SEEK_SET);
    bytesRead = read(fd, buffer, 32);
    if (bytesRead > 0)
    {
        buffer[bytesRead] = 0;
        puts(buffer);
    }
    return NULL;
}

void* write_routine()
int main()
{
    pthread_t th;
    const char* const numbers[] = { "one", "two", "three", "four", "five" };
    fd = open("file.txt", O_RDWR | O_CREAT | O_TRUNC, S_IRWXU | S_IRWXG);
    srand(time(NULL));

    read_offset = lseek(fd, SEEK_SET, 0);
    pthread_create(&th, NULL, reader_routine, NULL);
    for(int i = 0; i < 5; ++i)
    {
        flock(fd, LOCK_EX);
        sleep(rand()%5);
        lseek(fd, 0, SEEK_END);
        write(fd, numbers[i], strlen(numbers[i]));
        flock(fd, LOCK_UN);
    }
    q = 1;
    pthread_join(th, NULL);
    close(fd);
}
