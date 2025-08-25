CC     = gcc
BITS   = 64
ARCH   = native
MTUNE  = native
BIN    = main
SRC    = main.c
OPT    = fast
GDB    = 0
FLAGS  = -lglfw -lGL -lGLEW -lGLU -lm

all:
	$(CC) -m$(BITS) -march=$(ARCH) -mtune=$(MTUNE) -g$(GDB) -O$(OPT) -o $(BIN) $(SRC) $(FLAGS)

clean:
	rm -f $(BIN)
