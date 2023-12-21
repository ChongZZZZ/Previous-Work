#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <float.h>
#include <math.h>


__device__ double evaluateBoard(int* board, int size, int AI_role) {
    //inner ones get the most score
    //angles also get the score
    //printf("evaluating\n");
    double score=0;

    double center = (double) ((size-1)/2);

    double half_diagonal= sqrt(2*((double)(size/2)* (double)(size/2)));

    for(int i=0; i< size*size; i++){ //checking current status

        if(board[i]== AI_role){
            // weighted more for corner
            if(i==0 || i==(size-1)|| i == (size*size-1) || i == (size*(size-1))){ 
                score += half_diagonal*0.7;
            } else{ // weighted according to the distance from the center
            int x_int = i / size;
            double x = x_int;
            double y = i % size;
            score = score + half_diagonal - sqrt((x-center)*(x-center)+(y-center)*(y-center));
            }
        }    
    }

    // need to also consider the continuous



    return score;
}

// not full and no winner return 0
// winner == cross return 1
// winner == circle return 2
// full return 3
__device__ int winner_or_full(int* board, int size) {
    
    // Check horizontal and vertical stuff
    for (int i=0; i< size; i++){
        int potential_winner = board[i*size];
        
        bool horizontal= true;
        bool vertical=true;
        // Check for the winner horizontally
        for (int j=0; j < size; j++){
            if (board[i*size+j] != potential_winner){
                horizontal= false;
                break;
            }
        }

        if (horizontal){
            return potential_winner;
        }
        
        // Changing the potential winner to the vertical one
        potential_winner = board[i];
        
        // Check winner in the vertical
        for (int j=0; j < size; j++){
            if (board[j*size+i]!=potential_winner){
                vertical=false;
                break;
            }
        }

        if (vertical){
            return potential_winner;
        }
    }

    // Check // copy the board
      int* copy_board = (int*)malloc(sizeof(int) * size * size);

    for (int n = 0; n < size * size; n++) {
        copy_board[n] = board[n];
    }

    int potential_winner = board[0];
    if (potential_winner != 0){
        bool diagonal = true;

        for (int i=0; i < size; i++){
            if (board[i * size + i] != potential_winner) {
                diagonal = false;
                break;
            }
        }

        if (diagonal) {
            return potential_winner;
        }  
    }

    // Check the other diagonal
    potential_winner = board[size - 1];
    if (potential_winner != 0) {
        bool diagonal = true;

        for (int i = 0; i < size; i++) {
            if (board[i * size + (size - 1 - i)] != potential_winner) {
                diagonal = false;
                break;
            }
        }

        if (diagonal) {
            return potential_winner;
        }
    }

    // Check if the board is filled (cat's scratch)
    for (int i=0; i< size*size; i++){
        if(board[i]==0){
            //no winner and not filled
            return 0;
        }
    }

    return 3;
}

__device__ double MinMax(int* board, int Move, int size, int AI_role, bool Max) {

  int status = winner_or_full(board, size);



  if (status == 1 || status == 2) {  // cross is the winner
    // check whether it is AI
    if (AI_role == status) {
      return 10000;
    } else {
      return -10000;
    }

  } else if (status == 3) {  // board is filled and no winner (a tie)
    return 0;

  } else {
   
    double score = evaluateBoard(board, size, AI_role);
    //printf("evaluating score is %lf\n", score);
    return score;

  }


  // if(blockIdx.x==0 && (threadIdx.x * size + threadIdx.y==1)){
  // printf("xixi: for block %d and thread %d, status: %d\n", blockIdx.x, threadIdx.x * size + threadIdx.y, status);
  // }
 
  if (Max) {
    double bestValmax = -10000;  // evaluating the remaining cells

    // get all the empty cells
    for (int i = 0; i < size * size; i++) {
      if (board[i] == 1 || board[i] == 2) {  //< the board is occupied
        continue;
      }
      // copy the board
      int* copy_board = (int*)malloc(sizeof(int) * size * size);

      for (int n = 0; n < size * size; n++) {
        copy_board[n] = board[n];
      }

      // play the move (AI making the move)
      copy_board[i] = AI_role;

      // if(blockIdx.x==0 && (threadIdx.x * size + threadIdx.y==1)){
      //   for (int n = 0; n < size * size; n++){
      //     printf("In MAx value: %d\n", copy_board[n]);
      //   }
      // }

      bestValmax = fmax(bestValmax, MinMax(copy_board, i, size, AI_role, false));  // calculate the maximum of all the boards.
    }

    // printf("Best Value Max: %lf\n", bestValmax);

    return bestValmax;

  } else {
    double bestValmin = 10000;

    for (int i = 0; i < size * size; i++) {
      if (board[i] == 1 || board[i] == 2) {  // the board is occupied
        continue;
      }

      // copy the board
      int* copy_board = (int*)malloc(sizeof(int) * size * size);

      for (int n = 0; n < size * size; n++) {
        copy_board[n] = board[n];
      }

      // play the move (Human make the move)
      if (AI_role == 1) {
        copy_board[i] = 0;
      } else {
        copy_board[i] = 1;
      }

      // if(blockIdx.x==0 && (threadIdx.x * size + threadIdx.y==1)){
      //   for (int n = 0; n < size * size; n++){
      //     printf("In MIN value: %d\n", copy_board[n]);
      //   }
      // }

      bestValmin = fmin(bestValmin, MinMax(copy_board, i, size, AI_role, true));  // calculate the minimum of all the boards.
    }

    // printf("Best Value Min: %lf\n", bestValmin);
    return bestValmin;
  }
}




__global__ void minimaxKernel(int* board, int  board_size, int human_role, double* result) {
 
  // Make shared variables for calculating the best score
  __shared__ double*  score;
  int num = board_size*board_size;
  __shared__ int* step;

  if (threadIdx.x == 0){
    score = new double[num];
    step = new int[num];
  }

 

  // Each thread is one cell in the potential board
  int current_value = board[blockIdx.x*board_size*board_size+threadIdx.x * board_size + threadIdx.y];

  //printf("for block %d and thread %d, current_value 1: %d\n", blockIdx.x, threadIdx.x * board_size + threadIdx.y, current_value);

  // NOTE: Code doesn't go past here. 

  //The move that I want to play next
  int last_step = threadIdx.x * board_size + threadIdx.y;

  double current_score =  0;

  //If the space is not occupied
  if (current_value == 0) {

    // Copy the board
    int* copy_board = (int*)malloc(sizeof(int) * board_size * board_size);
    // Play another step in each copy board
    for (int n = 0; n < board_size * board_size; n++) {
      copy_board[n] = board[blockIdx.x*board_size*board_size+n];
    }

    // For the current possible move, assign it to the Human so that it
    // can evaluate whether it will be a good move or not
    copy_board[last_step] = human_role;
    //printf("xixi: for block %d and thread %d, current score: %lf and last_step: %d\n", blockIdx.x, threadIdx.x * board_size + threadIdx.y, current_score, last_step);
    if(blockIdx.x==0 && (threadIdx.x * board_size + threadIdx.y==1)){
      for (int n = 0; n < board_size * board_size; n++) {
        //printf("The board revised move: %d\n", copy_board[n]);
      }
    }

    // Default setting
    int AI_role = 0;

    //Get the AI's role
    if (human_role == 1) {
      AI_role = 2;
    } else {
      AI_role = 1;
    }
    //printf("hehe: for block %d and thread %d, current score: %lf and last_step: %d\n", blockIdx.x, threadIdx.x * board_size + threadIdx.y, current_score, last_step);

    // Do the min max algorithm
    current_score = MinMax(copy_board, last_step, board_size, AI_role, true);
    //printf("haha: for block %d and thread %d, current score: %lf and last_step: %d\n", blockIdx.x, threadIdx.x * board_size + threadIdx.y, current_score, last_step);

  } else {
    current_score = 0;
    last_step = -1;
  }

    //printf("for block %d and thread %d, current score: %lf and last_step: %d\n", blockIdx.x, threadIdx.x * board_size + threadIdx.y, current_score, last_step);
    // Sync all of the threads
    __syncthreads();
    score[threadIdx.x * board_size + threadIdx.y]= current_score;
    step[threadIdx.x * board_size + threadIdx.y]= last_step;
    __syncthreads();

    double max_score = -10000;
    if(threadIdx.x == 0 && threadIdx.y==0){
      for(int i = 0 ; i < board_size * board_size; i++){
        
        if(step[i]!=-1){
          if(score[i] > max_score){
            max_score = score[i];
          }
        }
      }
      result[blockIdx.x]= max_score;
    }

    __syncthreads();

    // if(threadIdx.x == 0 && threadIdx.y==0){
    //   printf("current score for the %d block is %lf\n", blockIdx.x, result[blockIdx.x]);
    // }

}

extern "C" __host__ int AI_run(int* board, int board_size, int AI_role){

    // Make array of <x> copies of the board to explore every first possible
    // move that the AI could make against the player
    // storing them all in one array
    int * next_move_board = (int*)malloc (sizeof(int)*board_size*board_size*board_size*board_size);

    

    // moves
    int move[board_size*board_size];

    for (int i=0; i< board_size*board_size; i++){
      move[i]=-1;
    }

    // Counter to count how many spaces the AI could make a move
    int possible_move=0;

    // Put the board copies in the array
    for(int i=0; i < board_size*board_size; i++){
        // If there is an open space
        if(board[i]==0){
            
            for (int n = 0; n < board_size * board_size; n++) {
                next_move_board[possible_move*board_size * board_size+n] = board[n];
            }

            // For the current possible move, assign it to the AI so that it
            // can evaluate whether it will be a good move or not
            next_move_board[possible_move* board_size * board_size+i] =AI_role;

            move[possible_move]= i;

            // Increment counter variable
            possible_move++;
        }


    }

    //printf("Potential move: %d\n", possible_move);

    // for (int i=0; i< board_size*board_size; i++){
    //   printf("CPU: %d \n", next_move_board[board_size*board_size*(possible_move-1)+i]);
    // }

    int human_role = 0;

    if(AI_role==1){
        human_role = 2;
    } else{
        human_role = 1;
    }

    int*  gpu_board;
    double *  gpu_result;
    int* gpu_role;
    int* gpu_board_size;
    

    // Allocate memory on the GPU for the flattened board
    // Allocate space for boards on the GPU
    if (cudaMallocManaged(&gpu_board, board_size * board_size * sizeof(int)* possible_move) != cudaSuccess) {
        fprintf(stderr, "Failed to allocate boards on GPU\n");
        exit(2);
    }

    // !!!!Score for each step
    if (cudaMallocManaged(&gpu_result, possible_move*sizeof(double)) != cudaSuccess) {
        fprintf(stderr, "Failed to allocate result on GPU\n");
        exit(2);
    }

    // Allocate role for roleprintf("hahaha\n");
    if (cudaMallocManaged(&gpu_role, sizeof(int)) != cudaSuccess) {
        fprintf(stderr, "Failed to allocate roles on GPU\n");
        exit(2);
    }

    // Allocate role for board_size
    if (cudaMallocManaged(&gpu_board_size, sizeof(int)) != cudaSuccess) {
        fprintf(stderr, "Failed to allocate board_size on GPU\n");
        exit(2);
    }


    // Copy the cpu's boards to the gpu with cudaMemcpy
    if (cudaMemcpy(gpu_board, next_move_board, board_size * board_size * sizeof(int)* possible_move, cudaMemcpyHostToDevice) !=
        cudaSuccess) {
        fprintf(stderr, "Failed to copy boards to the GPU\n");
    }

    // Copy the role
    if (cudaMemcpy(gpu_role, &human_role, sizeof(int), cudaMemcpyHostToDevice) !=
        cudaSuccess) {
        fprintf(stderr, "Failed to copy role to the GPU\n");
    }

    // Copy the board size
    if (cudaMemcpy(gpu_board_size, &board_size, sizeof(int), cudaMemcpyHostToDevice) !=
        cudaSuccess) {
        fprintf(stderr, "Failed to copy board_size to the GPU\n");
    }
    
    //Set up block
    dim3 threadsPerBlock(board_size, board_size);

    //dim3 threadsPerBlock(1,3);


    size_t numBlocks = possible_move;

    //size_t numBlocks = 1;

    minimaxKernel<<<numBlocks, threadsPerBlock>>> (gpu_board, *gpu_board_size, *gpu_role, gpu_result);

    
    // Wait for the GPU to finish
    if (cudaDeviceSynchronize() != cudaSuccess) {
        fprintf(stderr, "CUDA Error: %s\n", cudaGetErrorString(cudaPeekAtLastError()));
    }


    // place to store the result
    double* cpu_result = (double*) malloc (sizeof(double)*possible_move);

    

    // Transfer the result
    // Transfer the result back to the host
    // Should this be a board ?!
    if (cudaMemcpy(cpu_result, gpu_result, possible_move*sizeof(double), cudaMemcpyDeviceToHost) != cudaSuccess) {
        fprintf(stderr, "Failed to copy result from the GPU\n");
    }

    // printf("finish from the GPU\n");

    //data store in move suddenly changed ? Maybe some overlap?????


    double best_score = -10000;
    int best_move = 0;
    
  //  for (int i=0; i< possible_move; i++){
  //     printf("%lf\n", cpu_result[i]);
  //   }

    // Find the best move
    for (int i = 0; i < possible_move; i++) {
        if (cpu_result[i] > best_score) {
            best_score = cpu_result[i];
            best_move = move[i];
        }
    }

    // printf("best move: %d for score %lf\n", best_move, best_score);


    // Clean up
    cudaFree(gpu_board);
    cudaFree(gpu_result);
    cudaFree(gpu_role);
    cudaFree(gpu_board_size);


    return best_move; 
    
}


