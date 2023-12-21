#define _GNU_SOURCE
#include <openssl/md5.h>
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define MAX_USERNAME_LENGTH 64
#define PASSWORD_LENGTH 6
#define MAX_RANGE 26 * 26 * 26 * 26 * 26 * 26
#define STACK_EMPTY -1

/**
 * Generates the next candidate password based on the given candidate.
 *
 * This function generates the next candidate password by incrementing the characters
 * from 'a' to 'z' cyclically in the given candidate string.
 *
 * \param candidate  A character array representing the current candidate password.
 * \param length     The length of the candidate password.
 */
void generate_candidate(char* candidate, int length) {
  // If the candidate length is 0, there's nothing to generate, so return.
  if (length == 0) {
    return;
  }

  // Check if the last character in the candidate is less than 'z'.
  if (candidate[length - 1] < 'z') {
    // Increment the last character to the next lowercase letter.
    candidate[length - 1] = candidate[length - 1] + 1;
  } else {
    // If the last character is 'z', wrap around to 'a'.
    candidate[length - 1] = 'a';

    // Decrement the length and recursively generate the next candidate.
    length = length - 1;
    generate_candidate(candidate, length);
  }
}

/************************* Part A *************************/

/**
 * Find a six character lower-case alphabetic password that hashes
 * to the given hash value. Complete this function for part A of the lab.
 *
 * \param input_hash  An array of MD5_DIGEST_LENGTH bytes that holds the hash of a password
 * \param output      A pointer to memory with space for a six character password + '\0'
 * \returns           0 if the password was cracked. -1 otherwise.
 */
int crack_single_password(uint8_t* input_hash, char* output) {
  // Create the first candidate 'aaaaaa'
  char candidate[7];
  for (int i = 0; i < 6; i++) {
    candidate[i] = 'a';
  }
  candidate[6] = '\0';
  // Total number of combinations of passwords

  for (int i = 0; i < MAX_RANGE; i++) {
    uint8_t
        candidate_hash[MD5_DIGEST_LENGTH];  //< This will hold the hash of the candidate password
    MD5((unsigned char*)candidate, strlen(candidate), candidate_hash);  //< Do the hash

    // Now check if the hash of the candidate password matches the input hash
    if (memcmp(input_hash, candidate_hash, MD5_DIGEST_LENGTH) == 0) {
      // Match! Copy the password to the output and return 0 (success)
      strncpy(output, candidate, PASSWORD_LENGTH + 1);
      return 0;
    } else {
      // Try the next candidate if the current password does not match
      generate_candidate(candidate, PASSWORD_LENGTH);
    }
  }
  return -1;
}

/********************* Parts B & C ************************/

/**
 * This struct is the root of the data structure that will hold users and hashed passwords.
 *
 * This struct represents a username and its corresponding MD5 hash. The MD5 hash is
 * stored as a hexadecimal string, including the null-terminator.
 */
typedef struct password_pair {
  char* user;    // Username
  char md5[33];  // MD5 hash as a hexadecimal string (32 characters) + '\0'
  int cracked;   // Flag to indicate if the password was cracked
} password_pair_t;

/**
 * Structure to hold a set of password pairs and the number of passwords remain uncracked.
 *
 * This struct represents a collection of password pairs which used to store multiple
 * username and MD5 hash combinations. It also store number of password and number of password
 * remain uncracked.
 */
typedef struct password_set {
  password_pair_t* data;  // Array of password_pair_t
  int length;             // Number of password
  int remaining;          // NUmber of remaining password need to be cracked
} password_set_t;

/**
 * This structure holds thread-specific data required for password cracking.
 *
 * It contains pointers to the password set being processed, the start and end candidate passwords
 * for the current thread's range, and a count of passwords successfully cracked by this thread.
 */
typedef struct thread_data {
  // Pointer to the password set to be processed by this thread.
  password_set_t* passwords;
  // The start candidate password for this thread's range.
  char start_candidate[7];
  // The end candidate password for this thread's range.
  char end_candidate[7];
  // The count of passwords successfully cracked by this thread.
  int cracked_count;
} thread_data_t;

/**
 * Initialize a password set.
 *
 * \param passwords  A pointer to allocated memory that will hold a password set
 */
void init_password_set(password_set_t* passwords) {
  passwords->data = NULL;
  passwords->length = 0;
  passwords->remaining = 0;
}

/**
 * Add a password to a password set
 *
 * \param passwords   A pointer to a password set initialized with the function above.
 * \param username    The name of the user being added.
 * \param password_hash   An array of MD5_DIGEST_LENGTH bytes that holds the hash of this user's
 * password.
 */

void add_password(password_set_t* passwords, char* username, uint8_t* password_hash) {
  // Grow the data array
  passwords->data = realloc(passwords->data, sizeof(password_pair_t) * (passwords->length + 1));

  // Store the username
  passwords->data[passwords->length].user = strdup(username);

  // Store the MD5 hash
  memcpy(passwords->data[passwords->length].md5, password_hash, MD5_DIGEST_LENGTH);

  // Set the cracked flag to 0 for new passwords
  passwords->data[passwords->length].cracked = 0;
  // Increment the number of stored passwords
  passwords->length++;
  // Increment the number of passwords need to be cracked
  passwords->remaining++;
}

// Mutex for locking the password list
pthread_mutex_t password_mutex;

/**
 * Function executed by each thread to crack passwords.
 *
 * This function attempts to crack passwords within the candidate range for a thread and updates
 * the cracked count and prints the results when a password is cracked.
 *
 * \param arg  A pointer to thread-specific data containing password information.
 */
void* thread_crack(void* arg) {
  thread_data_t* data = (thread_data_t*)arg;
  char candidate[7];
  strncpy(candidate, data->start_candidate, 7);

  // Continuously generate candidates and check them until we reach the end candidate for this
  // thread or no more password need to be cracked
  do {
    uint8_t candidate_hash[MD5_DIGEST_LENGTH];
    MD5((unsigned char*)candidate, strlen(candidate), candidate_hash);
    size_t j = 0;

    // Iterate through the list of passwords to compare with the candidate hash
    while (j < data->passwords->length) {
      // check if the password match and the password is uncracked
      // <Since each thread has its own non-overlapping range, then if one thread crack a password,
      // no other thread can crack it. Thus, we do not need check whether the password is cracked by
      // other thread again once a matching password is found after acquire the lock.>
      if (memcmp(data->passwords->data[j].md5, candidate_hash, MD5_DIGEST_LENGTH) == 0 &&
          data->passwords->data[j].cracked == 0) {
        // Password successfully cracked
        pthread_mutex_lock(&password_mutex);  // Lock before accessing the passwords

        // Mark the password as cracked
        data->passwords->data[j].cracked = 1;
        // increment number of password cracked by the thread
        data->cracked_count++;
        // decrement number of password remain uncracked
        data->passwords->remaining--;
        printf("%s %s\n", data->passwords->data[j].user, candidate);

        // Unlock after accessing the passwords
        pthread_mutex_unlock(&password_mutex);

        // break if cracked a password
        break;
      } else {
        j++;
      }
    }

    // generate new candidate
    generate_candidate(candidate, PASSWORD_LENGTH);
  } while (strcmp(candidate, data->end_candidate) != 0 && data->passwords->remaining != 0);

  // Exit the thread when the cracking process is complete
  pthread_exit(NULL);
}

/**
 * Calculate the candidate range for a thread based on the thread number.
 *
 * This function computes the starting and ending candidates for a thread's password cracking
 * range based on the total number of possible candidates and the thread's position.
 *
 * \param start       A character array to store the starting candidate for the thread.
 * \param end         A character array to store the ending candidate for the thread.
 * \param thread_num  The number assigned to the thread (0, 1, 2, 3).
 */
void calculate_candidate_range(char* start, char* end, int thread_num) {
  // Calculate the total number of possible candidates

  // Calculate the candidate range per thread (assuming four threads in this example)
  int range_per_thread = MAX_RANGE / 4;

  // Calculate the starting candidate number for the current thread
  int start_num = range_per_thread * thread_num;

  // Calculate the ending candidate number for the current thread
  int end_num = range_per_thread * (thread_num + 1);

  // Generate the starting and ending candidates for the thread's range
  for (int i = PASSWORD_LENGTH - 1; i >= 0; i--) {
    start[i] = 'a' + (start_num % 26);
    end[i] = 'a' + (end_num % 26);
    start_num /= 26;
    end_num /= 26;
  }

  // Null-terminate the generated candidates
  start[PASSWORD_LENGTH] = '\0';
  end[PASSWORD_LENGTH] = '\0';
}

/**
 * Crack passwords using multiple threads.
 *
 * This function creates four threads to concurrently crack passwords by distributing the password
 * cracking range among them. It waits for all threads to finish their work and returns the total
 * number of cracked passwords.
 *
 * \param passwords  A pointer to the password set containing hashed passwords and other
 * informations.
 *
 * \returns          The total number of cracked passwords.
 */
int crack_password_list(password_set_t* passwords) {
  // Create and start 4 threads
  pthread_t threads[4];
  thread_data_t thread_data[4];

  // Initialize the mutex for synchronization
  pthread_mutex_init(&password_mutex, NULL);

  // Initialize thread-specific data and start threads
  for (int i = 0; i < 4; i++) {
    thread_data[i].passwords = passwords;
    thread_data[i].cracked_count = 0;

    // Calculate the candidate range for the current thread
    calculate_candidate_range(thread_data[i].start_candidate, thread_data[i].end_candidate, i);

    // Create a new thread to execute password cracking
    pthread_create(&threads[i], NULL, thread_crack, &thread_data[i]);
  }

  int total_cracked = 0;

  // Wait for all threads to finish
  for (int i = 0; i < 4; i++) {
    pthread_join(threads[i], NULL);

    // Accumulate the cracked password count from each thread
    total_cracked += thread_data[i].cracked_count;
  }

  // Clean up the mutex
  pthread_mutex_destroy(&password_mutex);

  return total_cracked;
}
/******************** Provided Code ***********************/

/**
 * Convert a string representation of an MD5 hash to a sequence
 * of bytes. The input md5_string must be 32 characters long, and
 * the output buffer bytes must have room for MD5_DIGEST_LENGTH
 * bytes.
 *
 * \param md5_string  The md5 string representation
 * \param bytes       The destination buffer for the converted md5 hash
 * \returns           0 on success, -1 otherwise
 */
int md5_string_to_bytes(const char* md5_string, uint8_t* bytes) {
  // Check for a valid MD5 string
  if (strlen(md5_string) != 2 * MD5_DIGEST_LENGTH) return -1;

  // Start our "cursor" at the start of the string
  const char* pos = md5_string;

  // Loop until we've read enough bytes
  for (size_t i = 0; i < MD5_DIGEST_LENGTH; i++) {
    // Read one byte (two characters)
    int rc = sscanf(pos, "%2hhx", &bytes[i]);
    if (rc != 1) return -1;

    // Move the "cursor" to the next hexadecimal byte
    pos += 2;
  }

  return 0;
}

void print_usage(const char* exec_name) {
  fprintf(stderr, "Usage:\n");
  fprintf(stderr, "  %s single <MD5 hash>\n", exec_name);
  fprintf(stderr, "  %s list <password file name>\n", exec_name);
}

int main(int argc, char** argv) {
  if (argc != 3) {
    print_usage(argv[0]);
    exit(1);
  }

  if (strcmp(argv[1], "single") == 0) {
    // The input MD5 hash is a string in hexadecimal. Convert it to bytes.
    uint8_t input_hash[MD5_DIGEST_LENGTH];
    if (md5_string_to_bytes(argv[2], input_hash)) {
      fprintf(stderr, "Input has value %s is not a valid MD5 hash.\n", argv[2]);
      exit(1);
    }

    // Now call the crack_single_password function
    char result[7];
    if (crack_single_password(input_hash, result)) {
      printf("No matching password found.\n");
    } else {
      printf("%s\n", result);
    }

  } else if (strcmp(argv[1], "list") == 0) {
    // Make and initialize a password set
    password_set_t passwords;
    init_password_set(&passwords);

    // Open the password file
    FILE* password_file = fopen(argv[2], "r");
    if (password_file == NULL) {
      perror("opening password file");
      exit(2);
    }

    int password_count = 0;

    // Read until we hit the end of the file
    while (!feof(password_file)) {
      // Make space to hold the username
      char username[MAX_USERNAME_LENGTH];

      // Make space to hold the MD5 string
      char md5_string[MD5_DIGEST_LENGTH * 2 + 1];

      // Make space to hold the MD5 bytes
      uint8_t password_hash[MD5_DIGEST_LENGTH];

      // Try to read. The space in the format string is required to eat the newline
      if (fscanf(password_file, "%s %s ", username, md5_string) != 2) {
        fprintf(stderr, "Error reading password file: malformed line\n");
        exit(2);
      }

      // Convert the MD5 string to MD5 bytes in our new node
      if (md5_string_to_bytes(md5_string, password_hash) != 0) {
        fprintf(stderr, "Error reading MD5\n");
        exit(2);
      }

      // Add the password to the password set
      add_password(&passwords, username, password_hash);
      password_count++;
    }

    // Now run the password list cracker
    int cracked = crack_password_list(&passwords);

    printf("Cracked %d of %d passwords.\n", cracked, password_count);

  } else {
    print_usage(argv[0]);
    exit(1);
  }

  return 0;
}