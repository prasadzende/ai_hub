import os
from dotenv import load_dotenv
from typing import Literal, Optional, Any
from pydantic import BaseModel, Field
from utils.config_loader import load_config
from openai import OpenAI
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama


class ConfigLoader:
    def __init__(self):
        print(f"Loaded config.....")
        self.config = load_config()
    
    def __getitem__(self, key):
        return self.config[key]

class ModelLoader(BaseModel):
    model_provider: Literal["groq", "openai", "ollama", "lmstudio"] = "groq"
    config: Optional[ConfigLoader] = Field(default=None, exclude=True)

    def model_post_init(self, __context: Any) -> None:
        self.config = ConfigLoader()
    
    class Config:
        arbitrary_types_allowed = True
    
    def load_llm(self):
        """
        Load and return the LLM model.
        """
        print("LLM loading...")
        print(f"Loading model from provider: {self.model_provider}")
        if self.model_provider == "groq":
            print("Loading LLM from Groq..............")
            groq_api_key = os.getenv("GROQ_API_KEY")
            model_name = self.config["llm"]["groq"]["model_name"]
            llm=ChatGroq(model=model_name, api_key=groq_api_key)
        elif self.model_provider == "openai":
            print("Loading LLM from OpenAI..............")
            openai_api_key = os.getenv("OPENAI_API_KEY")
            model_name = self.config["llm"]["openai"]["model_name"]
            llm = ChatOpenAI(model_name=model_name, api_key=openai_api_key)
        elif self.model_provider == "ollama":
            #openai_api_key = os.getenv("OPENAI_API_KEY")
            model_name = self.config["llm"]["ollama"]["model_name"]
            print(f"Loading model {model_name} from Ollama..............")
            llm = ChatOllama(model=model_name)
        elif self.model_provider == "lmstudio":
            print("Loading LLM from LMstudio..............")
            model_name = self.config["llm"]["lmstudio"]["model_name"]
            #llm = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
            llm = ChatOpenAI(model_name=model_name, api_key=os.getenv("lm-studio"), openai_api_base=os.getenv("LMSTUDIO_BASE_API"), temperature=0.7)
        return llm
    
    