import os
from langchain.tools import tool
from typing import List
from dotenv import load_dotenv
from openai import OpenAI
from vanna.openai.openai_chat import OpenAI_Chat
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore

llm = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self,client=None, config=None):
        OpenAI_Chat.__init__(self, client=llm, config=config)
        ChromaDB_VectorStore.__init__(self, config=config)

class VannaTool:
    def __init__(self, client=None, config=None):
        load_dotenv()
        self.vn = MyVanna(client, config)
        self.vn.connect_to_sqlite(os.getenv("SQLITE_DATABASE_PATH"))
        self.vanna_tool_list = self._setup_tools()
    
    def _setup_tools(self) -> List:
        """Setup all tools for vanna database search"""
        @tool
        def query_patient_db(question: str) -> str:
            """Search patient database using natural language query"""
            
            generated_sql = self.vn.generate_sql(question=question)
            
            if self.vn.is_sql_valid(sql=generated_sql):
                return "These are the details from database: " + str(self.vn.run_sql(sql=generated_sql))
            else:
                return "Could not generate valid SQL query for your question"
    
        return [query_patient_db]