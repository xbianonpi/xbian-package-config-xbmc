#!/bin/bash

case $1 in
    source-update)
        find . -name "*.py" | xargs xgettext --output=po/xbian-config.pot
        ;;
    source-upload)
        tx push -s
        ;;
    translations-download)
        tx pull -a
        ;;
    *)
        echo "Usage: $0 {source-update|source-upload|translations-download}"
        exit 1
esac

exit 0
