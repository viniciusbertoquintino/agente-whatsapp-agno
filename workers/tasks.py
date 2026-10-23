from celery import Celery, signals
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from redisvl.extensions.cache.llm import SemanticCache

from services.waha_service import send_message

app = Celery('tasks', broker='pyamqp://guest:guest@rabbitmq//')

agent = None
cache = None

@signals.worker_process_init.connect
def inicializar_recurso_global(**kwargs):
  global agent, cache

  with open("data/asimov.md", "r") as f:
    asimov_doc = f.read()

  with open("data/prompt.xml", "r") as f:
    prompt_doc = f.read()

  cache = connect_semantic_cache()

  agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),
    instructions="<fatos>" + "\n" + asimov_doc + "\n" + "</fatos>" + "\n" + prompt_doc
    )


@app.task
def task_answer(chat_id, prompt):
    
  if response := get_semanctic_cache_answer(cache=cache, prompt=prompt):
     message = f"(cache) {response}"
  else:
        message = get_ai_answer(prompt=prompt)   
        if message:
            print("RESPOSTA DA IA:", message)
            set_semanctic_cache_answer(cache=cache, prompt=prompt, answer=message)
        else:
           message = "Tente novamente mais tarde."

  send_message(chat_id, message)


def get_semanctic_cache_answer(cache: SemanticCache, prompt: str) -> str|None:
    
    response = cache.check(prompt=prompt)

    if len(response) == 0:
        return None
    
    return response[0]["response"]

def set_semanctic_cache_answer(cache: SemanticCache, prompt: str, answer: str) -> None:
    cache.store(
        prompt=prompt,
        response=answer
    )

def get_ai_answer(prompt:str) -> str | None:
  try:
    result = agent.run(input=prompt)
    return result.content
  except Exception as e:
    print("Exception:", e)


def connect_semantic_cache()-> SemanticCache:
  return SemanticCache(
    name="llmcache",
    ttl=360,
    redis_url="redis://redis:6379",
    distance_threshold=0.1
  )
