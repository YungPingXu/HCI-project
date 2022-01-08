echo "$1 $2 $3"
curl -v -X POST https://api.line.me/v2/bot/message/push \
-H 'Content-Type: application/json' \
-H 'Authorization: Bearer {'$1'}' \
-d '{ \
    "to": '$2', \
    "messages":[ \
        { \
            "type":"text", \
            "text":"@'$3'" \
        } \
    ] \
}'