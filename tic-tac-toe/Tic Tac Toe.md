# Ultimate Tic Tac Toe

_This project implements what we call "Ultimate Tic Tac Toe", which entails a board that can be **bigger** than the typical 3x3 board._

It supports both singleplayer and multiplayer options. 
* Singleplayer is run through the terminal 
* Multiplayer is run through a UI interface where the connecting user _(player 2)_ must enter in the server number and board size from the host.
* When choosing the space to play a space, you enter the space that you want in the following format: "\<row> \<column>"
* **The program supports boards from 3x3 to 8x8.**

## Description

The three concepts that this project involves are Parallelism with GPUs,
Parallelism with Threads, and Networks and Distributed Systems. 
* The **Parallelism with GPUS** will be included in the implementation of AI. When doing the Min-Max algorithm, the project will split the different tasks of board exploration to GPUs and let them further explore and do the score calculation of each score. 
    * The GPU returns the solution that has the higher score. 
    * The use of GPUs will speed up AI, especially with the large board size and with a larger number of steps to explore. 
* The **Networks and Distributed Systems** will be included in the implementation of the multiplayer scenario since the TicTacToe game with multiplayer is similar to the p2pchat. 
    * In this case, there will be only two people chatting with each other and the input of their chat will be the coordinates of the board and certain settings of the board.
    * Instead of receiving the input of the other player, the player will just the updated board, after the other makes a choice. 
* The **Parallelism with Threads** is included when implementing networking because the project will need threads to create connections with others and also threads to receive information and send information.

## Getting Started

### Dependencies

* _CUDA_ is required for this program to run.
* _Linux_ is required for the sockets to work properly.


### Executing program

##### Makefile:
```
make
```

##### First Player (multiplayer) and User (singleplayer):
```
./engine <username>
```

##### Second Player _(multiplayer only)_:
```
./engine <username> <peer> <port number>
```

## Help

If you are the second player connecting to the host, make sure to enter the correct board size. If not, you will run into some bad behavior by the program. If you do accidentally type in the wrong board size, then immediately type `:q` or `:quit` and reconnect to the host with the right board size.

## Authors

* Chong Zhao, Grinnell '25
* Sofia DiCarlo, Grinnell '25


## Acknowledgments

Inspiration, code snippets, etc.
* We borrowed ui.c, ui.h, and socket.h from Charlie Curtsinger (Grinnell College)