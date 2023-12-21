# GPU Sudoku Solver

_This project_ implements a program that uses the GPU to solve sudoku puzzles. This computation also lends itself well to the GPU: we have a lot of available parallelism within each puzzle, and you will solve many puzzles simultaneously.


### Dependencies

* _C_ is required for this program to run.
* _Cuda_ is required for this program to run.
* The repository includes a make file
 
 ### Instruction
 After making the file, running
 ```
./sudoku inputs/medium.csv
```
The user can solve the sudoku puzzles included in the inputs files

## Author

* Chong Zhao
* Jeronimo Camargo Ochoa

##  Acknowledgments

Thanks for the help and instruction from Professor Charlie Curtsinger
