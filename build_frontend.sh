#!/bin/sh

cd ./web/webApp

echo "BUild angular app"

ng build

cd ../../server

rm -rf ./webApp
mkdir ./webApp

cp ../web/webApp/dist/web-app/* ./webApp
