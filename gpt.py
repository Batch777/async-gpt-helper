import asyncio
from tools import one_call
from utils import handle_input
import argparse
import functools
import time


def async_timer(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} executed in {end - start:.4f} seconds")
        return result

    return wrapper


# @async_timer
async def main():
    parser = argparse.ArgumentParser(description="处理单个字符串参数的示例脚本")
    parser.add_argument(
        "input_string", type=str, default="", help="需要传入的字符串参数"
    )
    args = parser.parse_args()

    # handed_input = handle_input(args.input_string)
    answer = await one_call(args.input_string, "default", True)
    print(answer)


if __name__ == "__main__":
    asyncio.run(main())
