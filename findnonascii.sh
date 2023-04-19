#!/bin/sh

# find files from git index that contains non-usascii text
DEBUG=false

debugecho() {
if [ "$DEBUG" = true ]; then
    echo "DEBUG: $1"
  fi
}

# separator some command uses
IFS=$'\n'

# errors ocurred in a pipe will be returned
set -o pipefail 

ignorefile=".nonusasciiignore"
jogai_files=()
if [ -f $ignorefile ]; then
  readarray -t jogai_files < "$ignorefile"
fi

output=""

# create command line to $output
for t in "${jogai_files[@]}"; do
  if [ -z "$t" ]; then
    continue
  fi
  output+=" . ':!:$t'"
  debugecho "t is $t"
done

debugecho "output is $output"
command="git ls-files -- $output"
debugecho "command is $command"

for file in $(eval "$command"); do
  debugecho "$file"
  
  if [ -d "$file" ]; then
    echo "SKIP => $file is a directory"  
    continue
  fi

  output=$(sed '1s/^\xEF\xBB\xBF//' "$file" | tr -d '\000-\011\013-\177' | tr -d '©' | tr -d '\n' 2>&1 )
  if [ $? -ne 0 ]; then
    echo "Error: $output"
    exit 2
  fi

  # check empty
  if [ -z "$output" ]; then
    echo -n "OK => "
    echo $file
  else
    echo -n "ERROR => $file contains non-ASCII characters. => "
    echo "$output" | cut -c 1-255
    LC_ALL=C grep "$output" "$file"
    exit 1
  fi
done
