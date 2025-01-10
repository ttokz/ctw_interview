from datetime import datetime
from elasticsearch import Elasticsearch, helpers

# client = Elasticsearch("http://localhost:9200/")

class ESearchClient:
    def __init__(self):
        self.es = Elasticsearch("http://host.docker.internal:9200/")  # <-- connection options need to be added here
        client_info = self.es.info()
        print('Connected to Elasticsearch!')
        print(client_info.body)
        index_name = 'pdf-text'
        if not self.es.indices.exists(index=index_name):
            self.es.indices.create(
                index=index_name,
                mappings={
                    "properties": {
                        "doc_name": {"type": 'text'},
                        "doc_page": {"type": 'text'},
                        "text_vector": {
                            "type": "dense_vector",
                            "dims": 100,
                            "index": True,
                            "similarity": "cosine"
                        },
                        "doc_text": {
                            "type": "text"
                        }
                    }
                }
            )

    def bulk(self, document_list):
        helpers.bulk(self.es, document_list, index='pdf-text')

    def search(self, text, embedding, index="pdf-text", top_k: int=3):
        resp = self.es.search(
            index=index,
            query= {
                'bool': {
                    'must': {
                        'multi_match': {
                            'query': text,
                            'fields': ['review_text'],
                        }
                    }
                }
            },
            knn= {
                "field": "review_vector",
                "query_vector": embedding,
                "k": top_k,
            }
        )
        return resp