#!/bin/sh

# Chromeの安定最新バージョンを取得
CHROME_LATEST_VERSION=$(curl -sS "omahaproxy.appspot.com/linux?channel=stable")
echo "CHROME_LATEST_VERSION: ${CHROME_LATEST_VERSION}"

# Chromeの安定最新バージョンからメジャーバージョンを切り出す
CHROME_LATEST_MAJOR_VERSION=$(echo $CHROME_LATEST_VERSION | cut -d . -f 1)
echo "CHROME_LATEST_MAJOR_VERSION: ${CHROME_LATEST_MAJOR_VERSION}"

# Chromeの安定最新メジャーバージョンに合わせてChrome Driverの最新バージョンを取得
CHROME_DRIVER_VERSION=$(curl -sS "chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_LATEST_MAJOR_VERSION}")
echo "CHROME_DRIVER_VERSION: ${CHROME_DRIVER_VERSION}"

# Chrome Driver の最新バージョンをダウンロード
curl -O https://chromedriver.storage.googleapis.com/${CHROME_DRIVER_VERSION}/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
mv chromedriver /usr/local/bin/
rm -rf chromedriver_linux64.zip