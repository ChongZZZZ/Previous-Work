#include <errno.h>
#include <pthread.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <time.h>
#include <unistd.h>

// #include "multiplayer.h"
#include "socket.h"
#include "ui.h"
#include "ai.h"


#define MAX_USERNAME 63
#define MAX_MESSAGE 128

// Store the children of a peer
typedef struct child {
  int* port;
  size_t length;
  pthread_mutex_t lock;
} child_t;

pthread_mutex_t main_lock;

// Store the message (username+message)
typedef struct network_message {
  char username[MAX_USERNAME + 1];
  int message[MAX_MESSAGE];
} network_message_t;

// Username of this end
const char* username;

// Board size
int board_size;
// Board
int* board;
// The network fd of the parent node, used for communication
int parent_fd;

// A stack of this node's children
child_t children;

/**
 * Initialize the child
 * \param child child_t child struct to be initialized
 */
void child_init(child_t* child) {
  child->port = NULL;
  child->length = 0;
  pthread_mutex_init(&child->lock, NULL);
}

/**
 * Adding a port to the child struct
 * \param child child_t pointer to a child struct
 * \param port the port number needed to be added
 */
void child_add(child_t* child, int port) {
  pthread_mutex_lock(&child->lock);
  // Grow the data array
  child->port = realloc(child->port, sizeof(int) * (child->length + 1));

  // Put the value in
  child->port[child->length] = port;

  // Move the index of the top forward
  child->length++;
  pthread_mutex_unlock(&child->lock);
}

/**
 * Removing a port to the child struct
 * \param child child_t pointer to a child struct
 * \param port the port number needed to be removed
 */
int child_remove(child_t* child, int port) {
  pthread_mutex_lock(&child->lock);

  int to_return = -1;

  for (int i = 0; i < child->length; i++) {
    if (child->port[i] == port) {
      to_return = child->port[i];

      // Swap the to-be-removed position with the last item in the stack
      child->port[i] = child->port[child->length - 1];

      // Decrease the malloc'd space and length
      child->port = realloc(child->port, sizeof(int) * (child->length - 1));
      child->length--;

      // No further point in looping
      break;
    }
  }

  pthread_mutex_unlock(&child->lock);
  return to_return;
}

/** --------------------------------------------------------------------------*
*                                                                             *
*                   END OF LOCKS AND LINKED LIST FUNCTIONS                    *
*                                                                             *
*   --------------------------------------------------------------------------*
*/

// User Role
int role;

/**
* This function runs the singleplayer AI opponent
*
* \param board_size The size of the working board that the user specified
* \param role The role of the player, a.k.a: "x" or "o"
*/
void run_AI_mode(int board_size, int role);

/**
* This function runs the multiplayer mode, which runs the UI and creates a server
*
* \param board_size The size of the working board that the user specified
* \param username A string constant that stores the user's specified name
* \param server A string that stores the server that the connecting user specifies
* \param port_number The integer that stores the port number
*/
void run_multiplayer(int board_size, const char* username, char* server, unsigned short port_number);

/**
 * This is a void function that displays the rules for the player.
 *
 * \param option The option that the user enters to indicate whether they want
 * to read the rules or not.
 */
 void rules_interface(int option);

/**
* This function initializes the board
*
* \param board_size The size of the working board that the user specified
*/
void initializeBoard(int board_size);

/**
* This function makes the board empty (frees it)
*
* \param board_size The size of the working board that the user specified
*/
void freeBoard(int board_size);

/**
* This function checks if there is a winning pattern on the board.
*
* \param board The current board
*/
int check_win_status(int* board);

/**
* This function checks if we are checking something that is out of bounds of
* the board.
*
* \param board The current board being played
* \param x The x position of the current space
* \param y The y position of the current space
*/
bool out_bound_check(int* board, int x, int y);

/**
 * This function checks if there is an x or an o
 * in a specific location on the board.
 *
 * \param board The current board
 * \param x The x position
 * \param y The y position
 */
bool filled (int* board, int x, int y);

/**
* Function to check if the game has reached a tie.
* \param win_status If this is false, then check if the board is full
* \param board The current board being played
* \param x The x position of the current space
* \param y The y position of the current space
*/
bool is_cats_scratch(int* board);

/** --------------------------------------------------------------------------*
*                                                                             *
*                         END OF FUNCTION DECLARATIONS                        *
*                                                                             *
*   --------------------------------------------------------------------------*
*/

int main(int argc, char* argv[]) {
  // Checking the number of argument
  if (argc != 2 && argc != 4) {
    fprintf(stderr, "Usage: %s <username> [<peer> <port number>]\n", argv[0]);
    exit(1);
  }

  if (argc == 2) {
    // Print the friendly welcome message and board sample.
    printf(
        "\n 1 | 2 | 3 \n-----------\n 4 | 5 | 6 \n-----------\n 7 | 8 | 9 "
        "\n\n");
    printf("Welcome to Tic Tac Toe, Ultimate Edition!\n\n");
    printf(" - Would you like the rules?\n   1: yes\n   2: no\n\nOption: ");

    // Scan in the whether the user wants to read the rules or not.
    int rules_option = 0;
    scanf("%d", &rules_option);
    while((rules_option != 1) && (rules_option != 2)){
      printf("Please choose between 1 and 2\n");
      scanf("%d", &rules_option);
    }
    rules_interface(rules_option);

    // Entering in the board size
    int mode = 0;
    printf("Please enter the board size (3 - 8): ");
    scanf("%d", &board_size);
    while((board_size < 3) || (board_size > 8)){
      printf("Please choose between 3 and 8: \n");
      scanf("%d", &board_size);
    }


    printf("\n");

    // initialize the board
    initializeBoard(board_size);

    // Mode selection messages
    printf("Select mode:\n");
    printf(" 1: Multiplayer\n");
    printf(" 2: Singleplayer(AI)\n");
    printf(" 3: Quit\n");
    printf("\nOption: ");

    // Error check if the user did not pick a valid mode
    scanf("%d", &mode);
    while((mode != 1) && (mode != 2) && (mode != 3)){
      printf("Please choose between 1 and 3\n");
      scanf("%d", &mode);
    }

    // The user has chosen to exit
    if (mode == 3) {

      printf("\nGoodbye! See you next time!\n\n");
      exit(EXIT_SUCCESS);

    } else if (mode == 1){ // Default the first player as 'x'
      role = 1;
     } else {
      // Run this if the user chose singleplayer
      printf("Please choose cross (1) or circle (2): ");
      scanf("%d", &role);

      // Run this if the user chose something that is NOT 1 or 2
      while((role != 1) && (role != 2)){
      printf("Please choose between 1 and 2\n");
      scanf("%d", &role);
    }
     }
    // error message for incorrect input
    while (mode != 1 && mode != 2) {
      printf(
          "You have inputed an invalid option. Please pick between "
          "Multiplayer(1) and Singleplayer(2)\n");
      scanf("%d\n", &mode);
    }

    // If the user is player 1
    if (mode == 1) {
      printf(" You have selected multiplayer mode. Have fun! \n");
      printf("  -INFO: You are the first player. \n");
      username = argv[1];
      run_multiplayer(board_size, argv[1], NULL, -1);
    } else {
      run_AI_mode(board_size, role);
    }
  } else { //< If the user is player 2
    printf("  -INFO: You are the second player for tic-tac-toe!\n");
    unsigned short port_number = atoi(argv[3]);
    username = argv[1];
    initializeBoard(board_size);
    role = 2;
    //!!!! need to think of a way to update
    printf("Please enter the board size of the host: ");
    scanf("%d", &board_size);
    while((board_size < 3) || (board_size > 8)){
      printf("Please choose between 3 and 8: \n");
      scanf("%d", &board_size);
    }

    run_multiplayer(board_size, username, argv[2], port_number);
  }

  return 0;
}

/**
 * This is a void function that displays the rules for the player.
 *
 * \param option The option that the user enters to indicate whether they want
 * to read the rules or not.
 */
void rules_interface(int option) {
  // Have option to list the rules.
  if (option == 1) {
    printf("\n----RULES----\n");
    printf(
        " - This is like a normal game of Tic Tac Toe, but with a twist, which "
        "is that you\n   can make the (square) board as big as you want (with "
        "a minumum size of 3x3).\n");
    printf(
        " - To play a space for either mode, the player must enter the number "
        "of the corre-\n   sponding available space that they would like to "
        "put their x or o.\n");
    printf("-*SINGLEPLAYER*-\n");
    printf(
        " - You will play against an AI. You will first choose whether to play "
        "with x's or\n   o's, and then the player can select whether they go "
        "first or not.\n");
    printf(
        "   Then the game will play out where the player will take turns with "
        "the AI until\n   someone wins, or gets a 'cat's scratch' (tie). The "
        "player can play\n");
    printf(
        "   as many rounds as they want, and the program will keep track of "
        "how many wins\n   each player has. When the player chooses to quit, "
        "they will be given\n");
    printf(
        "   the amount of wins each player has, and who won the most "
        "rounds.\n");
    printf("-*MULTIPLAYER*-\n");
    printf(
        " - You will play against another human player, so you will be "
        "provided your port\n   number and board size for a friend to connect. "
        "Once player 2 is connected,\n");
    printf(
        "   the players will not have a choice of whether they play as “x” or "
        "“o”, rather\n   they will be assigned randomly. Also, the users will "
        "only have a choice\n");
    printf(
        "   of who goes first during the first round. The next round (if they "
        "choose to play\n   again), will have the person who lost the last one "
        "play first. The\n");
    printf(
        "   host and other player will have the choice to specify their "
        "username.\n");
    printf(" - The rest of the game plays out like singleplayer.\n\n");

  } else {
    printf("\nYou have chosen to skip the rules. Moving onto the game!\n\n");
  }
}

/**
* This function initializes the board
*
* \param board_size The size of the working board that the user specified
*/
void initializeBoard(int board_size) {
  board = (int*)malloc(board_size * board_size * sizeof(int*));
  for (int i = 0; i < board_size * board_size; i++) {
    board[i] = 0;
  }
}

/**
* This function makes the board empty (frees it)
*
* \param board_size The size of the working board that the user specified
*/
void freeBoard(int board_size) {
  if (board != NULL) {
    free(board);
    board = NULL;
  }
}

/**
* This function checks if a space will be displayed as containing an x, o, or
* a space character.
*
* \param space the board's current position
*/
void singleplayer_display_space(int space) {
  // Check if the space is an x or an o.
  if (space == 1) {
    printf(" x ");
    } else if (space == 2) {
    printf(" o ");
    } else {
    printf("   ");
    }
}
 
/**
* This function prints the board on the terminal for singleplayer mode.
*
* \param board The board that the player is playing against an AI.
*/
void print_singleplayer_board(int* board) {
 
     int rows = (board_size * 2) - 1;
 
     // Variable for properly printing rows
     int row_count = 0;
 
     printf("\n"); //< Newline for spacing
     for (int i = 0; i < rows; i++) { //< i is for printing rows
         for (int j = 0; j < board_size; j++) { //< j is for printing columns
 
             if (i % 2 == 0) { //< Print the main columns
                 // Display the x, o, or " "
                 singleplayer_display_space(board[row_count * board_size + j]);\
 
                 // Print the lines between each space
                 if (j != board_size - 1) printf("|");
 
             } else {
                 printf("---"); //< Print the lines in between
 
                 // Print the '+' for board style
                 if (j != board_size - 1)
                     printf("+");
             }
         }
        // Make it so that we only print spaces on odd row #'s
         if (i % 2 == 0) row_count++;
         // Add a newline
         printf("\n");
     }
     // Add a newline
     printf("\n");
}
 
/**
* This function sends messages to the network
*
* \param fd The file descriptor
* \param message The message that we are sending
*/
int send_network_message(int fd, network_message_t* message) {
  // If the message is NULL, set errno to EINVAL and return an error
  if (message == NULL) {
    errno = EINVAL;
    return -1;
  }

  // Write the entire username string
  size_t bytes_written = 0;
  while (bytes_written < (sizeof(char) * (MAX_USERNAME + 1))) {
    // Try to write the entire remaining message
    ssize_t rc = write(fd, message->username + bytes_written,
                       (MAX_USERNAME + 1) - bytes_written);

    // Did the write fail? If so, return an error
    if (rc <= 0) return -1;

    // If there was no error, write returned the number of bytes written
    bytes_written += rc;
  }

  // Write the entire message string
  bytes_written = 0;
  while (bytes_written < (sizeof(int) * (board_size * board_size))) {
    // Try to write the entire remaining message
    ssize_t rc =
        write(fd, message->message + bytes_written,
              ((board_size * board_size)) * sizeof(int) - bytes_written);

    // Did the write fail? If so, return an error
    if (rc <= 0) return -1;

    // If there was no error, write returned the number of bytes written
    bytes_written += rc;
  }

  ui_display("INFO", "Finish sending message");

  return 0;
}

/**
 * Receive a message across the network
 * \param fd int the fd_socket that we are reading from
 * \return network_message_t if we get a message or NULL if we get nothing
 */
network_message_t* receive_network_message(int fd) {
  network_message_t* result = malloc(sizeof(network_message_t));

  ui_display("INFO", "Try to receive message");

  // Try to read in the username
  size_t bytes_read = 0;
  while (bytes_read < MAX_USERNAME + 1) {
    // Try to read the entire remaining message
    ssize_t rc = read(fd, result->username + bytes_read,
                      (MAX_USERNAME + 1) - bytes_read);

    // Did the read fail? If so, return an error
    if (rc <= 0) {
      free(result);
      return NULL;
    }

    // Update the number of bytes read
    bytes_read += rc;
  }

  //ui_display("INFO", "haha");

  // Try to read in the message
  bytes_read = 0;
  while (bytes_read < (board_size * board_size) * sizeof(int)) {
    // Try to read the entire remaining message
    ssize_t rc = read(fd, result->message + bytes_read,
                      ((board_size * board_size)) * sizeof(int) - bytes_read);

    // Did the read fail? If so, return an error
    if (rc <= 0) {
      free(result);
      return NULL;
    }

    // Update the number of bytes read
    bytes_read += rc;
  }

  //ui_display("INFO", "Finish receiving message");

  return result;
}

/**
 * Receive a message from peer and pass the message to its children and parents
 * Working in threads
 * \param arg void pointer to the socket_fd, where we receive a message from
 * \return NULL
 */
void* receive_messages_from_peer(void* arg) {
  // initialize the client socket
  int socket_fd = *(int*)arg;

  // continually receive messages from any connected peers
  while (true) {
    network_message_t* message = receive_network_message(socket_fd);

    if (message == NULL) {
      ui_display("INFO", "Disconnected from peer");
      // remove the parent
      if (socket_fd == parent_fd) {
        parent_fd = -1;
      } else {
        // remove the child
        child_remove(&children, socket_fd);
      }

      return NULL;
    }

    // Update the board size after the move
    int winner = -1;
    bool tie = false;
    pthread_mutex_lock(&main_lock);
    for (int i = 0; i < board_size; i++) {
      for (int j = 0; j < board_size; j++)
        board[i * board_size + j] = message->message[i * board_size + j];
    }

    // Check the winner status
    winner = check_win_status(board);
    // Check if there is a tie
    tie = is_cats_scratch(board);
    // Unlock
    pthread_mutex_unlock(&main_lock);

    // Display the board
    ui_display_board(username, message->message, board_size);
    

    // Print end game message if there is a winner or a tie
    if(winner == 1 || winner == 2){
        ui_display("Game Over", "You lose");
        ui_display("If you want to quit", "Press :q");
        ui_display("If you want to continue", "Enter :n or :new");
    } else if (tie == true) {
      ui_display("Game Over", "Cat's Scratch!");
      ui_display("If you want to quit", "Enter :q or :quit");
      ui_display("If you want to continue", "Enter :n or :new");
    } else {
        ui_display("INFO", "This is your move.");
    }
    

    // send message to parent (if we have one)
    if ((parent_fd != -1) && (parent_fd != socket_fd)) {
      int rc = send_network_message(parent_fd, message);
      // remove the parent if it fails to send
      if (rc == -1) {
        parent_fd = -1;
      }
    }

    // send the message to child
    pthread_mutex_lock(&children.lock);
    for (int i = 0; i < children.length; i++) {
      if (socket_fd != children.port[i]) {
        int rc = send_network_message(children.port[i], message);
        // remove the child if it fails to send
        if (rc == -1) {
          pthread_mutex_unlock(&children.lock);
          child_remove(&children, children.port[i]);
          pthread_mutex_lock(&children.lock);
        }
      }
    }
    pthread_mutex_unlock(&children.lock);

    free(message);
  }
}

/**
 * Continually connecting to new peers
 *
 * Working in threads
 *
 * \param arg void a pointer to the socket_fd (our socket)
 * \return NULL
 */
void* connect_new_peers(void* arg) {
  // initialize the client socket
  int socket_fd = *(int*)arg;

  // continually accepting new connections
  while (true) {
    int peer_socket_fd = server_socket_accept(socket_fd);

    if (peer_socket_fd == -1) {
      perror("accept failed");
      exit(EXIT_FAILURE);
    }

    // Make thread to receive messages from peers
    pthread_t recv_thread;
    if (pthread_create(&recv_thread, NULL, receive_messages_from_peer,
                       &peer_socket_fd)) {
      perror("Failed to create thread to receive messages from peers");
      exit(EXIT_FAILURE);
    }

    child_add(&children, peer_socket_fd);
  }
}

/**
 * Run whenever the user hits enter after typing a message
 * \param message char* the message typed by the client
 */
void input_callback(const char* message) {
  if (strcmp(message, ":quit") == 0 || strcmp(message, ":q") == 0) {
    ui_exit();
  } else if (strcmp(message, ":new") == 0 || strcmp(message, ":n") == 0) {
    initializeBoard(board_size);
    ui_display("New Game", "Play again!");
  } else {
    //ui_display(username, message);

    char temp[4];
    strcpy(temp, message);
    temp[1] = '\0';
    // change the char to index
    int x = atoi(&temp[0]) - 1;
    int y = atoi(&temp[2]) - 1;

    if(filled(board,x,y)|| (out_bound_check(board,x,y))){
        ui_display("Invalid Input", "Put a real spot on the board this time!");
    } else{

    // Contruct the message with the info of username
    network_message_t network_message;
    strncpy(network_message.username, username, MAX_USERNAME);

    

    // Update the board size after the move
    int winner = -1;
    bool tie = false;
    pthread_mutex_lock(&main_lock);
    board[x * board_size + y] = role;
    for (int i = 0; i < board_size; i++) {
      for (int j = 0; j < board_size; j++)
        network_message.message[i * board_size + j] = board[i * board_size + j];
    }

    // Check the winner status
    winner = check_win_status(board);
    // Check if there is a tie
    tie = is_cats_scratch(board);
    // Unlock
    pthread_mutex_unlock(&main_lock);

    // Display the board
    ui_display_board(username, network_message.message, board_size);

    // Print end game message if there is a winner or a tie
    if (winner == 1 || winner == 2) {
      ui_display("Game Over", "You win");
      ui_display("If you want to quit", "Enter :q or :quit");
      ui_display("If you want to continue", "Enter :n or :new");
    } else if (tie == true) {
      ui_display("Game Over", "Cat's Scratch!");
      ui_display("If you want to quit", "Enter :q or :quit");
      ui_display("If you want to continue", "Enter :n or :new");
    }

    // Send the message to the relevant places
    // Send the message to parent
    if (parent_fd != -1) {
      // Send message to parent
      int rc = send_network_message(parent_fd, &network_message);

      // Remove the parent, if it fails to send the message
      if (rc == -1) {
        parent_fd = -1;
      }
    }

    // Send the message to child
    pthread_mutex_lock(&children.lock);
    for (int i = 0; i < children.length; i++) {
      int rc = send_network_message(children.port[i], &network_message);
      // Remove the child, if it fails to send the message
      if (rc == -1) {
        pthread_mutex_unlock(&children.lock);
        child_remove(&children, children.port[i]);
        pthread_mutex_lock(&children.lock);
      }
    }
    pthread_mutex_unlock(&children.lock);
  }
  }
}

/**
* This function runs the multiplayer mode, which runs the UI and creates a server
*
* \param board_size The size of the working board that the user specified
* \param username A string constant that stores the user's specified name
* \param server A string that stores the server that the connecting user specifies
* \param port_number The integer that stores the port number
*/
void run_multiplayer(int board_size, const char* username, char* server,
                     unsigned short port_number) {
  // Initialize the child
  child_init(&children);

  // Mark this thread as having no parent
  parent_fd = -1;

  // Set up a server socket to accept incoming connections
  unsigned short port = 0;
  int server_socket_fd = server_socket_open(&port);
  if (server_socket_fd == -1) {
    perror("Server socket was not opened");
    exit(EXIT_FAILURE);
  }

  // Start listening for connections, with a maximum of one queued connection
  if (listen(server_socket_fd, 1)) {
    perror("listen failed");
    exit(EXIT_FAILURE);
  }

  // If we have a specific server to connect to
  if ((server != NULL)) {
    // Unpack arguments
    char* peer_hostname = server;
    unsigned short peer_port = port_number;

    int socket_fd = socket_connect(peer_hostname, peer_port);
    if (socket_fd == -1) {
      perror("Failed to connect");
      exit(EXIT_FAILURE);
    }

    // Store who our parent is
    parent_fd = socket_fd;

    // Receive message from parent
    // Make thread to receive messages from peers
    pthread_t recv_thread_parent;
    if (pthread_create(&recv_thread_parent, NULL, receive_messages_from_peer,
                       &parent_fd)) {
      perror("Failed to create thread to receive messages from peers");
      exit(EXIT_FAILURE);
    }
  }

  // Make thread so we can connect to multiple peers
  pthread_t new_peers_thread;
  if (pthread_create(&new_peers_thread, NULL, connect_new_peers,
                     &server_socket_fd)) {
    perror("Failed to create thread to connect to new peers");
    exit(EXIT_FAILURE);
  }

  // Set up the user interface. The input_callback function will be called
  // each time the user hits enter to send a message.
  ui_init(input_callback);

  // Store our port in a string (of fixed length) so we can ui_display it
  // (we know this is weird it's the best we could come up with)
  char server_port[strlen("The server port is XXXXX") + 1];
  sprintf(server_port, "The server port is %5d", port);

  // Once the UI is running, you can use it to display log messages
  ui_display("INFO", server_port);


  char board_info[strlen("The board size is X") + 1];
  sprintf(board_info, "The board size is %1d", board_size);

  // Print the board size
  ui_display("INFO", board_info);

  // Run the UI loop. This function only returns once we call ui_stop()
  // somewhere in the program.
  ui_run();
}

/**
* This function runs the singleplayer AI opponent
*
* \param board_size The size of the working board that the user specified
* \param role The role of the player, a.k.a: "x" or "o"
*/
void run_AI_mode(int board_size, int role) {

  // Boolean to see if we play again
  bool play_again = true;

  while(play_again){
    //initialize the board
    initializeBoard(board_size);

    int AI_role = -1;

    // Make sure that the AI doesn't have the same role as the player
    if (role == 1){
      AI_role = 2;
    }else{
      AI_role = 1;
    }

    // Print the empty board to begin
    print_singleplayer_board(board);

    while (check_win_status(board)==0){ //!!! need to add outbound check and add tie situation
      printf("Your move!\n\n");
      int row = -1;
      int column = -1; 
      scanf("%d %d", &row, &column);
      while(filled(board,row-1, column-1)||out_bound_check(board,row-1, column-1)){
        printf("\nInvalid input, try again:\n\n");
        scanf("%d %d", &row, &column);
      }

      board[(row-1) *board_size+(column-1)]= role;
      // Print board after first move
      print_singleplayer_board(board);

      // Check to see if we continue
    if(check_win_status(board)==0){
      int AI_move= AI_run(board, board_size, AI_role);
      board[AI_move]= AI_role;
      printf("The AI has played:\n");
      print_singleplayer_board(board);
    }
  }

  // Variables for generating a random silly message
  time_t t;
  srand((unsigned) time (&t));

    if (check_win_status(board)==3){
        printf("There is a tie\n");
    } else if (check_win_status(board)==AI_role){
      // Print silly messages from the AI
      if (rand() % 4 == 0) {
        printf("The AI has won! Bow down to technology pleb.\n\n");
      } else if (rand() % 4 == 1) {
        printf("Oh no, you've let the AI win. How silly of you.\n\n");
      } else if (rand() % 4 == 2) {
        printf("You lost! The AI has won, and is very happy about it.\n\n");
      } else if (rand() % 4 == 3) {
        printf("Ha! You lose, the AI is victorious!\n\n");
      } else {
        printf("Pity. If you would have won this round you would have gotten a free T.J. Maxx gift card.\n\n");
      }
    } else {
        printf("You have won, Congrats!\n\n");
    }

    freeBoard(board_size);

    printf("Do you want to play again? (1 for play, 2 for quit): ");
    int choice;
    scanf("%d", &choice);
    if(choice==1){
      play_again= true;
    } else if(choice==2){
      play_again=false;
    } else{
      printf("Giving invalid input, quitting the game.\n");
    }
  }
}


/**
* This function checks if there is a winning pattern on the board.
*
* \param board The current board
*/
int check_win_status(int* board){
  
  // Check the columns and rows for winners
  for (int i=0; i< board_size; i++){
        int potential_winner = board[i*board_size];

        bool horizontal= true;
        bool vertical=true;

        // Check horizontally for a winner
        for (int j=0; j < board_size; j++){
            if (board[i*board_size+j] != potential_winner){
                horizontal= false;
                break;
            }
        }

        if (horizontal){
            return potential_winner;
        }

        // Changing the potential winner to the vertical one
        potential_winner = board[i];

        // Check vertically for a winner
        for (int j=0; j < board_size; j++){
            if (board[j*board_size+i]!=potential_winner){
                vertical=false;
                break;
            }
        }

        if (vertical){
            return potential_winner;
        }
    }
  
    // Check diagonal from top left to bottom right
    int potential_winner = board[0];
    if (potential_winner != 0){
        bool diagonal = true;

        for (int i=0; i < board_size; i++){
            if (board[i * board_size + i] != potential_winner) {
                diagonal = false;
                break;
            }
        }

        if (diagonal) {
            return potential_winner;
        }  
    }

    // Check the other diagonal
    potential_winner = board[board_size - 1];
    if (potential_winner != 0) {
        bool diagonal = true;

        for (int i = 0; i < board_size; i++) {
            if (board[i * board_size + (board_size - 1 - i)] != potential_winner) {
                diagonal = false;
                break;
            }
        }

        if (diagonal) {
            return potential_winner;
        }
    }

    // Check if the board is filled (cat's scratch)
    for (int i=0; i< board_size*board_size; i++){
        if(board[i]==0){
            //no winner and not filled
            return 0;
        }
    }

    return 3;
  }

/**
 * This function checks if there is an x or an o
 * in a specific location on the board.
 *
 * \param board The current board
 * \param x The x position
 * \param y The y position
 */
bool filled(int* board, int x, int y) {
  int index = x * board_size + y;

  if (board[index] != 1 && board[index] != 2) {
    return false;
  } else {
    return true;
  }
}

/**
* This function checks if we are checking something that is out of bounds of
* the board.
*
* \param board The current board being played
* \param x The x position of the current space
* \param y The y position of the current space
*/
bool out_bound_check(int* board, int x, int y){

    if((x>(board_size-1))|| (y>(board_size-1))){
        return true;
    }

    return false;
}

/**
* Function to check if the game has reached a tie.
* \param win_status If this is false, then check if the board is full
* \param board The current board being played
* \param x The x position of the current space
* \param y The y position of the current space
*/
bool is_cats_scratch(int* board) {
  
  // Counter variable for number of filled spaces
  int num_filled = 0;

  // Count how many filled spaces there are
  for (int i = 0; i < board_size; i++) {
    for (int j = 0; j < board_size; j++) {
      // If the space is filled, count it. 
      if (filled (board, i, j) == true) {
        num_filled++;      
      }
    }
  }

  // Check if the board is both filled and in there is not a winner.
  if (num_filled == board_size*board_size && check_win_status(board) == false) {
    // If so, then there is a cat's scratth, so return true.
    return true;
  } else return false;
}
