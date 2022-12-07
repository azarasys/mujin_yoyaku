#!/bin/bash

source ./param/secrets.sh

richmenus=$(curl -s -X GET https://api.line.me/v2/bot/richmenu/list -H 'Authorization: Bearer '$CHANNEL_ACCESS_TOKEN | jq -r ' .richmenus[].richMenuId')

for id in ${richmenus[@]};
do
    curl -X DELETE https://api.line.me/v2/bot/richmenu/$id -H 'Authorization: Bearer '$CHANNEL_ACCESS_TOKEN
done