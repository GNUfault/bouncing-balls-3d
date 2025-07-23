CC     = gcc
BITS   = 32
ARCH   = i686
BIN    = main
SRC    = main.c
OPT    = 3
FLAGS  = -lglfw -lGL -lGLEW -lGLU -lm

all:
	$(CC) -m$(BITS) -march=$(ARCH) -O$(OPT) -o $(BIN) $(SRC) $(FLAGS)

clean:
	srm -f $(BIN)
