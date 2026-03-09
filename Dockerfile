# CryptPad CTF – Docker Environment
#
# Build:
#   docker build -t cryptpad-ctf .
#
# Run the C++ solver:
#   docker run --rm cryptpad-ctf ./solver
#
# Run the Python solver:
#   docker run --rm cryptpad-ctf python3 decrypt_flag.py
#
# Interactive shell:
#   docker run --rm -it cryptpad-ctf bash

FROM gcc:latest

WORKDIR /app

# Copy all project files
COPY . .

# Compile the C++ tools
RUN g++ -std=c++17 -O2 -Wall -Wextra -o solver CTF_2026.cpp && \
    g++ -std=c++17 -O2 -Wall -Wextra -o encrypt encrypt_flag.cpp

# Ensure Python 3 is available
RUN apt-get update && apt-get install -y --no-install-recommends python3 && \
    rm -rf /var/lib/apt/lists/*

# Default command: run the C++ solver
CMD ["./solver"]
