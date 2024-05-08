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

void* writer_routine(fileP)
{
    FILE *fin, *fout;
    unsigned char *BufContent = NULL;
    BufContent = (unsigned char*) malloc(FILE_BLOCK_SIZE);
    size_t BufContentSz;

    if((fin=fopen("E:\\aa.txt", "rb")) == NULL){
        perror("fopen");
        exit(EXIT_FAILURE);
    }
    if((fout=fopen("E:\\bb.txt", "wb")) == NULL){
        perror("fopen");
        exit(EXIT_FAILURE);
    }

    while ((BufContentSz = fread(BufContent, sizeof(unsigned char), FILE_BLOCK_SIZE, fin)) > 0) 
    {
        fwrite(BufContent, sizeof(unsigned char), BufContentSz, fout);
    }

    fclose(fout);
    fclose(fin);

    delete BufContent;

}

int main(int argc, char *argv[])
{
    int opt; 
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
