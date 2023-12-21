#define _XOPEN_SOURCE
#define _XOPEN_SOURCE_EXTENDED

#include "scheduler.h"

#include <assert.h>
#include <curses.h>
#include <stdbool.h>
#include <ucontext.h>

#include "util.h"

// This is an upper limit on the number of tasks we can create.
#define MAX_TASKS 128

// This is the size of each task's stack memory
#define STACK_SIZE 65536

typedef enum { BLOCKED, SLEEPIN } state_t;
// This struct will hold the all the necessary information for each task
typedef struct task_info {
  // This field stores all the state required to switch back to this task
  ucontext_t context;

  // This field stores another context. This one is only used when the task
  // is exiting.
  ucontext_t exit_context;

  state_t status;
  bool finish;

  // true if blocked
  bool block;
  // true if sleeping
  bool sleep;

  // Stores wakeup time
  size_t wakeup_time;

  // True if waiting
  bool wait;

  // Stores the index of the job that's on wait
  int waitjob;

  // input check-- true if waiting for an unput
  bool wait_input;

  int user_input;

  //      read input, you will need to save it here so it can be returned.
} task_info_t;

int current_task = 0;          //< The handle of the currently-executing task
int num_tasks = 1;             //< The number of tasks created so far
task_info_t tasks[MAX_TASKS];  //< Information for every task

/**
This is a wrapper function for swapcontext that cycles through all the tasks.
It changes all the fields inside the struct as required, blocks when needed to, and unblocks as it cycles
It then calls swapcontext and goes to the next task in a round--robin fashion to the nearest unnblocked task
*/
void wrapper_swapcontext() {
  bool swapped = false;
  while (!swapped) {
    for (int i = 0; i < num_tasks; i++) {
      // Changing status
      if ((!tasks[i].finish) && tasks[i].block) {
        // Blocked tasks
        if (tasks[i].wait && tasks[tasks[i].waitjob].finish) {
          // Changing wait statues
          tasks[i].wait = false;
          tasks[i].block = false;
        }
        size_t current_time = time_ms();
        
        // Handle sleeping 
        if (tasks[i].sleep && (tasks[i].wakeup_time < current_time)) {
          tasks[i].sleep = false;
          tasks[i].block = false;
        }
        
        // Handle character input
        if ((tasks[i].wait_input)) {
          int c = getch();
          if (c != ERR) {
            tasks[i].wait_input = false;
            tasks[i].user_input = c;
            tasks[i].block = false;
          }
        }
      }
    }

     //Cycle through tasks and swapcontext it as its unblocked 
    for (int i = 0; i < num_tasks; i++) {
      if ((!tasks[i].finish) && (!tasks[i].block)) {
        int temp = current_task;
        current_task = i;
        swapped = true;
        swapcontext(&tasks[temp].context, &tasks[current_task].context);
      }
    }
  }
}

/**input
 * Initialize the scheduler. Programs should call this before calling any other
 * functiosn in this file.
 */
void scheduler_init() {
  //initialize the first task (main)
  tasks[0].wait = false;
  tasks[0].sleep = false;
  tasks[0].wait_input = false;
  tasks[0].block = false;
  tasks[0].finish = false;
  tasks[0].user_input = -1;
  tasks[0].wakeup_time = 0;
  tasks[0].waitjob = -1;
}

/**
 * This function will execute when a task's function returns. This allows you
 * to update scheduler states and start another task. This function is run
 * because of how the contexts are set up in the task_create function.
 */
void task_exit() {
  tasks[current_task].finish = true;
  wrapper_swapcontext();
  return;
}

/**
 * Create a new task and add it to the scheduler.
 *
 * \param handle  The handle for this task will be written to this location.
 * \param fn      The new task will run this function.
 */
void task_create(task_t* handle, task_fn_t fn) {
  // Claim an index for the new task
  int index = num_tasks;
  num_tasks++;

  // Set the task handle to this index, since task_t is just an int
  *handle = index;

  tasks[index].wait = false;
  tasks[index].sleep = false;
  tasks[index].wait_input = false;
  tasks[index].waitjob = -1;
  tasks[index].block = false;
  tasks[index].wakeup_time = 0;
  tasks[index].finish = false;
  tasks[index].user_input = -1;

  // We're going to make two user_inputt with the second

  // First, duplicate the current context as a starting point
  getcontext(&tasks[index].exit_context);

  // Set up a stack for the exit context
  tasks[index].exit_context.uc_stack.ss_sp = malloc(STACK_SIZE);
  tasks[index].exit_context.uc_stack.ss_size = STACK_SIZE;

  // Set up a context to run when the task function returns. This should call task_exit.
  makecontext(&tasks[index].exit_context, task_exit, 0);

  // Now we start with the task's actual running context
  getcontext(&tasks[index].context);

  // Allocate a stack for the new task and add it to the context
  tasks[index].context.uc_stack.ss_sp = malloc(STACK_SIZE);
  tasks[index].context.uc_stack.ss_size = STACK_SIZE;

  // Now set the uc_link field, which sets things up so our task will go to the exit context when
  // the task function finishes
  tasks[index].context.uc_link = &tasks[index].exit_context;

  // And finally, set up the context to execute the task function
  makecontext(&tasks[index].context, fn, 0);
}

/**
 * Wait for a task to finish. If the task has not yet finished, the scheduler should
 * suspend this task and wake it up later when the task specified by handle has exited.
 *
 * \param handle  This is the handle produced by task_create
 */
void task_wait(task_t handle) {
  // Block this task until the specified task has exited.
  tasks[current_task].wait = true;
  tasks[current_task].waitjob = handle;
  tasks[current_task].block = true;
  //swap context
  wrapper_swapcontext();
  return;
}

/**
 * The currently-executing task should sleep for a specified time. If that time is larger
 * than zero, the scheduler should suspend this task and run a different task until at least
 * ms milliseconds have elapsed.
 *
 * \param ms  The number of milliseconds the task should sleep.
 */
void task_sleep(size_t ms) {
  // Block this task until the requested time has elapsed.

  // Set the current task to sleep=true and block the task
  tasks[current_task].sleep = true;
  size_t wakeup_time = time_ms() + ms;
  tasks[current_task].wakeup_time = wakeup_time;
  tasks[current_task].block = true;

  //swap context
  wrapper_swapcontext();

  return;
}

int task_readchar() {
  // To check for input, call getch(). If it returns ERR, no input was available.
  // Otherwise, getch() will returns the character code that was read.

  //get the input
  int c = getch();

  //if no input is avaliable
  if (c == ERR) {
    //block and swap context
    tasks[current_task].wait_input = true;
    tasks[current_task].block = true;
    wrapper_swapcontext();
  }
  //return the input
  return tasks[current_task].user_input;
}
