CFLAGS=-std=c11 -Wall -Wextra -Werror -O1 -fsanitize=address,undefined -I../include
test: ; $(CC) $(CFLAGS) ../aquavia_metering.c test_metering.c -o /tmp/test_metering -lm && /tmp/test_metering
