#include <stdio.h>
#include <stdlib.h>
#include <strings.h>

struct ringbuffer{
    int size;
    int used;
    char *buffer;
    int head;
    int tail;
};
typedef struct ringbuffer ringbuffer_t;

ringbuffer_t *create_ringbuffer(int size){
    ringbuffer_t *new = malloc(sizeof(ringbuffer_t));
    if(!new){
        return NULL;
    }
    new->buffer = malloc(size);
    if(!new->buffer){
        return NULL;
    }
    new->size = size;
    new->used = 0;
    new->head = 0;
    new->tail = 0;
    return new;
}

void ringbuffer_put(ringbuffer_t *rb, void *elem, int size){
    //Create elem as "byte object"
    char *belem = (char *) elem;
    
    if(rb->head + size + sizeof(int) >= rb->size){
        //Handle overlapping size
        if(rb->size - rb->head < sizeof(int)){
            //Header has to wrap around
            bcopy(&size, &rb->buffer[rb->head], rb->size - rb->head);
            rb->head = 0;
            bcopy(&((char *) &size)[rb->size - rb->head], &rb->buffer[rb->head], sizeof(int) - (rb->size - rb->head));
            rb->head += sizeof(int) - (rb->size - rb->head);
            //Write elem to buffer
            bcopy(elem, &rb->buffer[rb->head], size);
            rb->head += size;
        }else{
            //Write size of elem to buffer
            bcopy(&size, &rb->buffer[rb->head], sizeof(int));
            rb->head += sizeof(int);
            bcopy(elem, &rb->buffer[rb->head], rb->size - rb->head);
        }
    }else{
        //Write size of elem to buffer
        bcopy(&size, &rb->buffer[rb->head], sizeof(int));
        rb->head += sizeof(int);
        //Write elem to buffer
        bcopy(elem, &rb->buffer[rb->head], size);
        rb->head += size;
    }
    
}


int main()
{
    printf("Hello World");

    return 0;
}
