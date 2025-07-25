import getpass
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

# from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()


models = [
    "meta-llama/llama-4-scout-17b-16e-instruct",
]

if "GROQ_API_KEY" not in os.environ:
    os.environ["GROQ_API_KEY"] = getpass.getpass("GROQ_API_KEY")

hugging_token: str = os.environ["HUGGINGFACE_TOKEN"]

llm = ChatGroq(
    model= models[0],
    temperature=0.9,
    max_tokens=None,
    timeout=None,
    max_retries=2

)



# model_name = "sentence-transformers/all-mpnet-base-v2"
# model_kwargs = {'device': 'cpu', 'token': hugging_token}
# encode_kwargs = {'normalize_embeddings': False}
# embeddings  = HuggingFaceEmbeddings(
#     model_name=model_name,
#     model_kwargs=model_kwargs,
#     encode_kwargs=encode_kwargs,
# )