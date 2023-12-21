CC := nvcc
CFLAGS := -g 

all: engine

clean:
	rm -f engine

engine: engine.c ai.cu ui.c ui.h socket.h
	$(CC) $(CFLAGS) -o engine engine.c ai.cu ui.c -lform -lncurses -lpthread

zip:
	@echo "Generating tic_tac_toe.zip file for sharing..."
	@zip -q -r tic_tac_toe.zip . -x .git/\* .vscode/\* .clang-format .gitignore engine
	@echo "Done. tic_tac_toe.zip is ready to share."
