# Worm Game

_This project_ implements implement a simple system for running a series of tasks within one process. Tasks in this system will run separate functions, and the scheduler will need to switch between them.

The scheduler that this program implemented support the game  **Worm!**, a clone of the classic game  _Snake_.

This game implementation uses several tasks:
1.  A main task that starts up the game
2.  A task to update the worm state in the game board
3.  A task that redraws the board periodically
4.  A task that reads input from the user and processes controls
5.  A task that generates “apples” at random locations on the board
6.  A task that updates existing “apples” by spinning them and removing them after some time


### Dependencies

* _C_ is required for this program to run.
* The repository includes a make file
 
 ### Instruction
 After making the file, running
 ```
./worm
```
The user can solve the sudoku puzzles included in the inputs files

## Author

* Chong Zhao
* Sauryanshu Khanal

##  Acknowledgments

Thanks for the help and instruction from Professor Charlie Curtsinger
