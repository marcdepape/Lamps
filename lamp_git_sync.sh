#!/bin/sh
UPDATE=$(git remote update)
echo $UPDATE
PULL=$(git pull)
echo $PULL
