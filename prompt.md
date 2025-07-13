现在我需要构建一个基于openai api的聊天系统，我需要以下功能：
1. 设计一个简约的前端对话界面，用于展示聊天内容和输入框。
2. 使用openai api进行聊天内容的生成和处理。
3. 实现一个后端服务，处理前端请求并与openai api进行交互。
4. 参照tests/openai_api_test.ipynb实现多个对话的方式：
    - 无需search的对话工具, 直接参考【3. 创建 Thread 进行对话】；
    - 需要带search的对话，外部维护一个session_id，通过手动传入对话历史来保证上下文的连贯性；其中带search的工具参考【 4. 测试web_search】```response = client.responses.create(
    model="gpt-4.1",
    tools=[{"type": "web_search_preview"}],
    input="What is the weather of Hangzhou today?"
)

print(response.output_text)```
5. 前端界面需要支持发送和接收消息，显示聊天记录。
6. 可以自己定义会话的system prompt, 以及每一轮对话的user prompt；system prompt通过配置文件传入，定义不同的前端接口，匹配不同的system prompt;
8. 在用户进入前端对话界面后，需要在左上角生成一个唯一的身份标识，并且该身份标识将在对话中保持不变，后端需要根据该身份标识存储和管理对话数据。
9. 系统需要支持对话的中断和恢复，用户可以在任何时候暂停对话，并在稍后继续。
10. 前端需要有一个清晰的用户界面，能够显示当前对话状态和历史消息。
11. 如果系统调用api失败，需要向用户报错，并提供重试的选项。
12. 在src/chat_tool目录下创建整个项目，并在tests目录下创建测试用例，确保所有功能正常工作。

# search
- 修改整个search_assistant的实现逻辑，不要使用openai的self.client.beta.assistants.create，因为assistant不支持web_search的使用；web_search需要使用client.responses.create来实现。
```
response = client.responses.create(
    model="gpt-4.1",
    tools=[{"type": "web_search_preview"}],
    input="What is the weather of Hangzhou today?"
)

print(response.output_text)```
以及，该assistant也需要支持多轮对话的上下文传递，所以需要在每次发送消息时，手动传入对话历史。

- 我需要做几个不同的link（接口），比如一个link对应的是普通对话，一个link对应的是带search的对话；每个link对应的system prompt也不同。

- 我不需要有一个选择助手类型的前置页面（因为我不希望用户知道他使用的是什么助手），直接进入对话界面即可。
    - 一个固定的link会对应到具体的对话接口，包括
        - 普通对话
        - 带search的对话
        - 普通对话且不带system prompt
    - 当用户进入对话界面时，系统会根据link自动加载对应的system prompt；并且自动生成相应的会话ID。


- 修改前端的显示方式
    - 整个显示区域更宽；
    - 每个消息框的宽度更宽；
    - 直接按enter的时候不要发送消息；
    - 更简洁；提示不要斜体；

- 另外需要改善当前的对话保存的机制，在对话界面设计一个对话完成的按钮，当用户点击以后，会提示用户他的会话id，以及将所有的会话内容以会话id为文件名保存为json文件；