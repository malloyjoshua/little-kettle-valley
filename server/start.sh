#!/bin/zsh
# Start the Cozy Tech Pack server. Uses the project JDK, never system Java.
cd "$(dirname "$0")"
JAVA="../tools/jdk17/Contents/Home/bin/java"
exec "$JAVA" @user_jvm_args.txt @libraries/net/minecraftforge/forge/1.20.1-47.4.10/unix_args.txt nogui "$@"
