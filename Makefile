CC      = gcc
MARCH   = native
MTUNE   = native
BIN     = main
SRC     = main.c
OPT     = fast
GDB     = 0
FLAGS   = -Wall -Wextra
LDFLAGS = -lglfw -lGL -lGLEW -lGLU -lm
CFLAGS  = -march=$(MARCH) -mtune=$(MTUNE) -g$(GDB) -O$(OPT) $(FLAGS)

all:
	$(CC) $(CFLAGS) -o $(BIN) $(SRC) $(LDFLAGS)
	strip -s $(BIN)

clean:
	rm -f $(BIN)

.PHONY: all clean
