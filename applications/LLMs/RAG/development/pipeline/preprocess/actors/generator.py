import ray

@ray.remote(
    num_gpus = 1
)
class Generator:
    def __init__(
        self,
        embedding_model: str,
        keyword_model: str
    ):
        import torch
        from langchain_huggingface import HuggingFaceEmbeddings
        import spacy

        print('Starting generator')
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print('GPU device: ' + str(device))
        
        print('Embedding model setup')
        self.embedding_model = HuggingFaceEmbeddings(
            model_name = embedding_model,
            model_kwargs = {
                "device": device
            }
        )
        print('Embedding model ready')
        
        spacy.require_gpu()

        print('Language model setup')
        self.language_model = spacy.load(
            name = keyword_model
        )
        print('Language model ready')

    def batch_create_embeddings(
        self,
        batched_chunks: any
    ) -> any:
        #batched_chunks = ray.get(batched_chunks_ref)
        batched_embeddings = []
        for tuple in batched_chunks:
            try: 
                list_index = tuple[0]
                chunks = tuple[-1]
                embeddings = self.embedding_model.embed_documents(
                    texts = chunks
                )
                batched_embeddings.append((list_index, embeddings))
            except Exception as e:
                print(e)
        batched_embeddings_ref = ray.put(batched_embeddings)
        return batched_embeddings_ref
    
    def batch_search_keywords(
        self,
        batched_text: any
    ):  
        #batched_text = ray.get(batched_text_ref)
        batched_keywords = []
        for tuple in batched_text:
            try: 
                list_index = tuple[0]
                text = tuple[-1]
                lowered = text.lower()
                formatted = self.language_model(lowered)
                keywords = [
                    token.lemma_ for token in formatted
                    if not token.is_stop               
                    and not token.is_punct              
                    and not token.is_space              
                    and len(token) > 1                  
                ]
                keywords = list(set(keywords))
                batched_keywords.append((list_index, keywords))
            except Exception as e:
                print(e)
        batched_keywords_ref = ray.put(batched_keywords)
        return batched_keywords_ref