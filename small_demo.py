import os
import asyncio
from openai import AsyncOpenAI
import time
import functools


client = AsyncOpenAI()


def async_timer(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} executed in {end - start:.4f} seconds")
        return result

    return wrapper


async def translate_text(text: str) -> str:
    """
    异步调用 AsyncOpenAI 接口，对单个字符串进行翻译。
    这里的 prompt 指示模型将输入文本翻译为中文。
    """
    # 这里用 "gpt-4o" 模型（如示例中所用），也可以根据需要替换为其它模型
    messages = [{"role": "user", "content": text}]
    response = await client.chat.completions.create(model="gpt-4o", messages=messages)
    return response.choices[0].message.content


async def translate_list(text_list: list) -> list:
    """
    并发翻译列表中所有字符串
    """
    tasks = [translate_text(text) for text in text_list]
    translations = await asyncio.gather(*tasks)
    return translations


@async_timer
async def main():
    sample_texts = [
        "Hello, how are you?",
        "This is a test sentence.",
        "Please translate this text.",
    ]
    translations = await translate_list(sample_texts)
    for original, translation in zip(sample_texts, translations):
        print(f"原文: {original}\n翻译: {translation}\n")


if __name__ == "__main__":
    asyncio.run(main())
