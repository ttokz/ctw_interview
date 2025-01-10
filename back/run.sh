docker run -p 9200:9200 -e "discovery.type=single-node" -e "xpack.security.enabled=false" -e "xpack.security.http.ssl.enabled=false" docker.elastic.co/elasticsearch/elasticsearch:8.13.4
docker build -t ctw_back .
docker run -p 8000:80 -v $(pwd)/:/code ctw_back