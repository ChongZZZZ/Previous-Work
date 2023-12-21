#include <errno.h>
#include <fcntl.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>

// This is the maximum number of arguments your shell should handle for one command
#define MAX_ARGS 128

/**
 * Struct that represents a command
 * \member token String that represents a command
 * \member wait Whether we need to wait for this command to finish execution
 */
typedef struct command {
  char* string;
  bool wait;
} command_t;

/**
 * Trims leading and trailing whitespace of a string
 *
 * \cite https://saturncloud.io/blog/best-algorithm-to-strip-leading-and-trailing-spaces-in-c/
 */
void trim_whitespace(char* string) {
  int start = 0;
  int end = strlen(string) - 1;

  // Trim leading whitespace
  while (string[start] == ' ') {
    start++;
  }

  // Trim trailing whitespace
  while (string[end] == ' ') {
    end--;
  }

  // Terminate new string
  string[end + 1] = '\0';

  // Move the trimmed substring to the beginning of the string
  memmove(string, string + start, end - start + 2);
}

/**
 * Splits the string from the command line by either ';' or '&
 *
 * \param commands Array of command_t structs that represent commands
 * \param str String input from command line
 * \return Length of the array to save space in main
 *
 * \cite Adapted from Chalie's code from the lab instructionss
 */
int split_string_into_commands(command_t* commands[], char* str) {
  // Trim leading and trailing whitespace
  trim_whitespace(str);

  int num_commands = 0;
  while (true) {
    // Call strpbrk to find the next occurrence of a delimeter
    char* delim_position = strpbrk(str, "&;");

    // If no more tokens, add null terminator and return
    if (delim_position == NULL) {
      commands[num_commands] = NULL;
      return num_commands;
    }

    // Save delimiter for later and terminate the token
    char delim = *delim_position;
    *delim_position = '\0';

    // Ignore empty command
    if (strcmp(str, "") == 0) continue;

    // Initialize command and store it
    // If delimiter is `&`, command needs to be waited for
    command_t* command = malloc(sizeof(command));
    command->string = str;
    command->wait = (delim == '&');
    commands[num_commands] = command;

    // Increment past delimiter and increment command count
    str = delim_position + 1;
    num_commands++;
  }
}

/**
 * Parses a string representing a command into space-separated tokens
 *
 * \param tokens Array of tokens extracted from a command
 * \param str Command input by user that needs to be processed
 *
 * \cite https://c-for-dummies.com/blog/?p=1769; clarification on strsep
 */
void parse_command(char** tokens, char* str) {
  // Trim leading and trailing whitespace
  trim_whitespace(str);

  // Repeatedly read and add tokens to array
  char* token = strsep(&str, " ");
  int length = 0;
  while (token != NULL) {
    tokens[length] = token;
    token = strsep(&str, " ");
    length++;
  }

  // Add the tailing NULL
  tokens[length] = token;
}

/**
 * Runs a command by spawning a child process to execute it.
 * Waits for command if is instructed to by `command_t->wait`
 *
 * \param command Struct representing a command
 */
void run_single_command(command_t* command) {
  // Parse command
  char* tokens[MAX_ARGS];
  parse_command(tokens, command->string);

  // Run cd
  if (strcmp(tokens[0], "cd") == 0) {
    chdir(tokens[1]);
    return;
  }

  // Run exit
  if (strcmp(tokens[0], "exit") == 0) {
    exit(EXIT_SUCCESS);
  }

  // Create child process to run any other command
  pid_t child_id = fork();

  // Failed to create child process
  if (child_id == -1) {
    perror("Fork failed \n");
    exit(EXIT_FAILURE);
  }

  // In child process, execute command
  if (child_id == 0) {
    // Exec only returns when error
    int rc = execvp(tokens[0], tokens);
    if (rc == -1) {
      perror("Exec failed");
      exit(EXIT_FAILURE);
    }

    // In parent process
  } else {
    if (command->wait) return;

    // Suspend execution and wait for child
    int status;
    pid_t rc = waitpid(child_id, &status, 0);

    // Failed to wait for child process
    if (rc == -1) {
      perror("wait failed");
      exit(EXIT_FAILURE);
    }

    // Child successfully exited
    if (WIFEXITED(status)) {
      printf("[%s exited with status %d]\n", tokens[0], WEXITSTATUS(status));
      return;
    }
  }
}

/**
 * Collects dead child processes until there are none left
 */
void collect_dead_child_processes() {
  int status;
  pid_t rc = waitpid(-1, &status, WNOHANG);

  // Find any child process that has ended
  // Return code 0 means no child status is available yet
  while (rc > 0) {
    if (WIFEXITED(status)) {
      printf("[background process %d exited with status %d]\n", rc, WEXITSTATUS(status));
    }
    rc = waitpid(-1, &status, WNOHANG);
  }
}

/**
 * Runs the program to simulate a shell
 *
 * @cite Code for child processes creation from Charlie
 */
int main(int argc, char** argv) {
  // If there was a command line option passed in, use that file instead of stdin
  if (argc == 2) {
    // Try to open the file
    int new_input = open(argv[1], O_RDONLY);
    if (new_input == -1) {
      fprintf(stderr, "Failed to open input file %s\n", argv[1]);
      exit(1);
    }

    // Now swap this file in and use it as stdin
    if (dup2(new_input, STDIN_FILENO) == -1) {
      fprintf(stderr, "Failed to set new file as input\n");
      exit(2);
    }
  }

  char* line = NULL;     // Pointer that will hold the line we read in
  size_t line_size = 0;  // The number of bytes available in line

  // Loop forever
  while (true) {
    // Collect any dead child processes
    collect_dead_child_processes();

    // Print the shell prompt
    printf("$ ");

    // Get a line of stdin, storing the string pointer in line
    if (getline(&line, &line_size, stdin) == -1) {
      if (errno == EINVAL) {
        perror("Unable to read command line");
        exit(2);
      } else {
        // Must have been end of file (ctrl+D)
        printf("\nShutting down...\n");

        // Exit the infinite loop
        break;
      }
    }

    // Replace newline character with `;`
    // If a command has no terminating `;` or `&`, this treats it correctly
    // Else, the empty command between the double `;;` or `&;` is discarded
    line[strlen(line) - 1] = ';';

    // Split the command line by ';' or `&` into smaller commands
    // This discards any empty or whitespace-only commands
    command_t* commands[MAX_ARGS];
    int num_commands = split_string_into_commands(commands, line);

    // Run the commands
    for (int i = 0; i < num_commands; i++) {
      run_single_command(commands[i]);
    }
  }

  // If we read in at least one line, free this space
  if (line != NULL) {
    free(line);
  }

  return 0;
}