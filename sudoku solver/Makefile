CC := nvcc
CFLAGS := -g

all: sudoku .extract-inputs

clean:
	rm -f sudoku

sudoku: sudoku.cu util.h Makefile
	$(CC) $(CFLAGS) -o sudoku sudoku.cu

.extract-inputs:
	tar xvzf inputs.tar.gz
	touch .extract-inputs

zip:
	@echo "Generating sudoku.zip file to submit to Gradescope..."
	@zip -q -r sudoku.zip . -x .git/\* .vscode/\* .clang-format .gitignore sudoku inputs.tar.gz inputs/\*
	@echo "Done. Please upload sudoku.zip to Gradescope."

format:
	@echo "Reformatting source code."
	@clang-format -i --style=file $(wildcard *.c) $(wildcard *.h) $(wildcard *.cu)
	@echo "Done."

.PHONY: all clean zip format

