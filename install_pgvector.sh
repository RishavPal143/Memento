#!/bin/bash
echo "Installing pgvector..."
cd /Users/rishav/Desktop/Memento/pgvector_src
sudo make install PG_CONFIG=/Library/PostgreSQL/18/bin/pg_config CPPFLAGS="-isysroot /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk" LDFLAGS="-isysroot /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk"
echo "Installation complete!"
