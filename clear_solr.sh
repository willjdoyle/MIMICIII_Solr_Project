#!/bin/bash
curl -X POST -H 'Content-Type: application/json' \
    'http://localhost:8983/solr/mimiciii/update?commit=true' \
    -d '{ "delete": {"query":"*:*"} }'
