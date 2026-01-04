import re
import uuid
import re
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain.chat_models import init_chat_model
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Define the model
#model = ChatOpenAI(base_url="http://127.0.0.1:1234/v1", api_key="not-needed", model="qwen/qwen3-8b")
model = init_chat_model(model_provider="openai", base_url="http://127.0.0.1:1234/v1", api_key="not-needed", model="qwen/qwen3-8b", verbose=True)

def node_start(state: MessagesState):
    print("node start...")
    question = state["messages"][-1].content
    return {"messages": [AIMessage(content=f"你的问题是：{question}")]}

def call_model(state: MessagesState):
    print("start call model...")
    #response = model.invoke(state["messages"])
    template = """
    你是一个智能助手，你的任务是回答用户的问题。
    
    # 用户问题
    {question}

    # 输出要求：
    - 保持回答的简洁性，字数控制在150字以内。
    - 输出内容不允许出现 <think>、<reasoning> 等多余标记。
    """
    prompt = PromptTemplate(template=template, input_variables=["question"])
    chain = prompt | model | StrOutputParser()
    
    question = state["messages"][-1].content
    response = chain.invoke({"question": question})
    cleaned_msg = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL | re.IGNORECASE).strip()
    
    return {"messages": [AIMessage(content=cleaned_msg)]}

graph = StateGraph(MessagesState)
graph.add_node("start", node_start)
graph.add_node("model", call_model)
graph.add_edge(START, "start")
graph.add_edge("start", "model")
graph.add_edge("model", END)
graph = graph.compile()

if __name__ == "__main__":
    config = {
        "configurable": {
            "thread_id": str(uuid.uuid4()),
        }
    }

    question = "北京奥运会的开幕时间"
    state = MessagesState(messages=[HumanMessage(content=question)])

    #result_state = graph.invoke(state, config=config)
    #for message in result_state.get("messages", []):
    #    message.pretty_print()
    
    for chunk in graph.stream({"messages": [HumanMessage(content=question)]}):
        print("="*20)
        print(f"\nchunk: {chunk}\n")