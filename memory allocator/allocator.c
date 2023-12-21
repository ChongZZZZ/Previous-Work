#define _GNU_SOURCE

#include <assert.h>
#include <malloc.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <unistd.h>

// The minimum size returned by malloc
#define MIN_MALLOC_SIZE 16
//The verfication of a page came from the allocator
#define MAGIC_NUMBER 1571605839
//The maximum size
#define MAX_SMALL_SIZE 2048
// The size of a single page of memory, in bytes
#define PAGE_SIZE 0x1000
// Round a value x up to the next multiple of y
#define ROUND_UP(x, y) ((x) % (y) == 0 ? (x) : (x) + ((y) - (x) % (y)))

//contructing a page header used for size checking and boundary checking
typedef struct page_header_t {
    long magic;
    size_t object_size;
} page_header_t;

//checking which size block that the ptr is in
size_t xxmalloc_usable_size(void* ptr);


// A utility logging function that definitely does not call malloc or free
void log_message(char* message);

//a free list (linked list) storing the avaliable number of blocks that can be allocated
//for a certain size
typedef struct free_object_t {
    struct free_object_t* next;
} free_object_t;

//The freelist of difference sizes
free_object_t* freelists[8]; // 16, 32, 64, 128, 256, 512, 1024, 2048


/**
  * \brief This fucntion rounds the size up to power of two
  * \param size the initial size that needs to be round up
  * \return size_t the round-up result
  */
size_t round_up_to_power_of_two(size_t size) {
    size_t power_of_two = 16; // Start with the smallest size class

    //If the size is larger than the current power of two
    //times the current power of two by two
    while (size > power_of_two) {
        power_of_two *= 2;
    }

    return power_of_two;
}


/**
  * \brief This fucntion rounds the size up to the closest multiple of page size
  * \param size the initial size that needs to be round up
  * \return size_t the round-up result
  */
size_t round_up_to_multiple_of_page_size(size_t size) {
    size_t multiple_of_page_size = PAGE_SIZE;
    int i = 1;

    //If the size is larger than the current power of two
    //add page_size to the multiple_of_page_size
    while (size > multiple_of_page_size) {
      multiple_of_page_size = PAGE_SIZE*i;
      i++;
    }

    return multiple_of_page_size;
}


/**
  * \brief Transiting the size to the index of corresponding free list
  * \param size the number of byte
  * \return int the corresponding index of freelist of that size in the freelist array
  */
int size_to_index(size_t size) {
    int sizes[] = {16, 32, 64, 128, 256, 512, 1024, 2048};
    for (int i = 0; i < 8; i++) {
        if (size <= sizes[i]) {
            return i;
        }
    }
    return -1; // size is too large
}

/**
 * Allocate space on the heap.
 * \param size  The minimium number of bytes that must be allocated
 * \returns     A pointer to the beginning of the allocated space.
 *              This function may return NULL when an error occurs.
 */
void* xxmalloc(size_t size) {
  //Rounding up the object size
  if (size <= MAX_SMALL_SIZE){
    size = round_up_to_power_of_two(size);
  }else{
    size = round_up_to_multiple_of_page_size(size);
  }

  //Finding the corresponding index of freelist corresponding of the size
  int index = size_to_index(size);

  //Case 1: The rounded-up size is larger than 2048
  if (size > MAX_SMALL_SIZE) {
    //directly allocate the memory
    void* block = mmap(NULL, size, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (block == MAP_FAILED) {
      log_message("mmap failed! Giving up.\n");
      exit(2);
    }
    return block;
  }

  //Case 2: The rounded-up size is smaller than or equal to 2048
  //Checking whether we initialize the corresponding freelist
  if (freelists[index] != NULL) {
    free_object_t* obj = freelists[index];
    freelists[index] = obj->next;
    return (void*)obj;
  }
  else {
    //Assigning space for the freelist
    void* block = mmap(NULL, PAGE_SIZE, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (block == MAP_FAILED) {
      log_message("mmap failed! Giving up.\n");
      exit(2);
    }

    //Create the header block at the head of the allocated space
    page_header_t* header = (page_header_t*)block;
    header->magic = MAGIC_NUMBER;
    header->object_size = size;

    //Calculate the avaliable blocks in the page and create the free list
    int num_objects = (PAGE_SIZE - size) / size; //Calculate number of blocks can be created without the header
    free_object_t* prev = NULL;
    for (int i = 0; i < num_objects; i++) {
      //skip the header plus the addtional i blocks ahead
      free_object_t* obj = (free_object_t*)((char*)block + size + i * size);
      if (prev) {
        prev->next = obj; //build up the list
      } else {
        freelists[index] = obj; //link the freelist to the freelist arrau
      }
      prev = obj;
    }

    if (prev) {
      prev->next = NULL;
    }

    //Get the first element of the corresponding freelist
    free_object_t* obj = freelists[index];
    freelists[index] = obj->next; //delete it from the freelist
    return (void*)obj;
  }
}

/**
 * Free space occupied by a heap object.
 * \param ptr   A pointer somewhere inside the object that is being freed
 */
void xxfree(void* ptr) {
  //determine which block-size that this ptr belongs to
  size_t size = xxmalloc_usable_size(ptr);

  //We use xxmalloc_usable_size to check if ptr is NULL or the magic number does not match
  //If size is 0, then return nothing
  if (size==0) return;

  //transit to freelist index
  int index = size_to_index(size);
  //get the block
  free_object_t* obj = (free_object_t*)ptr;
  //put it back to freelist
  obj->next = freelists[index];
  freelists[index] = obj;

}

/**
 * Get the available size of an allocated object. This function should return the amount of space
 * that was actually allocated by malloc, not the amount that was requested.
 * \param ptr   A pointer somewhere inside the allocated object
 * \returns     The number of bytes available for use in this object
 */
size_t xxmalloc_usable_size(void* ptr) {
  // If ptr is NULL always return zero
  if (ptr == NULL) return 0;
  intptr_t address = (intptr_t)ptr;
  //Finding the address of the page of the ptrs
  intptr_t page_start = address - (address % PAGE_SIZE);
  page_header_t* header = (page_header_t*)page_start;
  //Checking whether the page belongs to the allocator
  if (header->magic != MAGIC_NUMBER) return 0;
  //Return the data store in the header block of the page
  return header->object_size;
}


/**
 * Print a message directly to standard error without invoking malloc or free.
 * \param message   A null-terminated string that contains the message to be printed
 */
void log_message(char* message) {
  // Get the message length
  size_t len = 0;
  while (message[len] != '\0') {
    len++;
  }

  // Write the message
  if (write(STDERR_FILENO, message, len) != len) {
    // Write failed. Try to write an error message, then exit
    char fail_msg[] = "logging failed\n";
    write(STDERR_FILENO, fail_msg, sizeof(fail_msg));
    exit(2);
  }
}
