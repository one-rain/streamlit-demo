import sys
from unittest import IsolatedAsyncioTestCase, TestCase
import uuid

from langchain_core.messages import HumanMessage

from agent.data_agent import graph2
from agent.barley_agent import graph1


class TestAgent(TestCase):

    @classmethod
    def setUpClass(cls):
        # 类级别的前置条件设置，整个类运行最先只执行一次
        print("setUpClass")
        print("Python解释器路径:", sys.executable)
        print("\n依赖路径:", sys.path)

    # 测试前的初始化工作（每个测试方法执行前都会调用）
    def setUp(self):
        # 测试方法级别的前置条件设置，所有测试方法运行前都执行一次
        print("\nstarting...")

    def test_simple_agent_graph(self):
        config = {
            "configurable": {
                "thread_id": str(uuid.uuid4()),
            }
        }

        question = "表格"
        #result_state = graph.invoke(state, config=config)
        #for message in result_state.get("messages", []):
        #    message.pretty_print()
        
        for chunk in graph1.stream({"messages": [HumanMessage(content=question)]}, config=config):
            print("="*20)
            print(f"\nchunk: {chunk}\n")

    
    def test_data_agent_graph(self):
        config = {
            "configurable": {
                "thread_id": str(uuid.uuid4()),
            }
        }

        question = "表格"        
        for chunk in graph2.stream({"messages": [HumanMessage(content=question)]}, config=config):
            print("="*20)
            print(f"\nchunk: {chunk}\n")

# python -m unittest tests.agent.common_test.TestAgent.test_simple_agent_graph
