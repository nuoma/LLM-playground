# Created by nuo on 20230614, with help from GPT3.5z
# This code generate questions based on a given book material, then generate answers using GPT3.5
# reference from https://github.com/MediaBrain-SJTU/MedicalGPT-zh

import os
import json
import time
from multiprocessing import Pool, Lock
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import re
import openai
from progress.bar import Bar

lock = Lock()

# Configuration
openai.api_key = ""
bookdatapath = "./SafetyEngineer4Books.json" #3323行，160万字，注册中级安全工程师化工方向共4本教科书。
output_filepath = "./SafetyEngineer4Books_generated_qa.json"
openai.proxy = "http://127.0.0.1:7890" # request thru VPN
#api_keys = ["API_KEY_1", "API_KEY_2", "API_KEY_3"]  # if you have multiple keys

# Azure OpenAI API Configuration
# openai.api_type = "azure"
# openai.api_base = ""
# openai.api_version = "2023-03-15-preview"
# openai.proxy = "http://127.0.0.1:7890"

with open(bookdatapath, "r") as f:
    book_list = json.load(f)

if os.path.exists(output_filepath):
    with open(output_filepath, "r") as f:
        generate_task = json.load(f)
else:
    generate_task = {}

data_list = list(set(range(len(book_list))) - set(generate_task.keys()))
print("Number of books to generate QA: ", len(data_list))

bar = Bar('Processing', max=len(data_list), suffix='%(index)d/%(max)d - %(percent).1f%% - %(elapsed)ds- %(eta)ds')


def parse_response(original):
    questions = original.split('\n')
    result = []
    for question in questions:
        question = re.sub(r'[0-9].\s*', '', question)
        if len(question) > 5:
            result.append(question)
    return result


def gpt_generate(it):
    global count
    input_book = book_list[it]

    prompt = f"指南：\n{input_book}\n"
    prompt += f"请根据上述文本中与化工知识相关的内容与逻辑关系提出几个中文问题。注意，提出的问题应该提供充实的内容，使问题具有挑战性。问题数量要多。每个问题要细致且准确。问题需要用比较口语化的简单的表述。问题类型应该是多样化的。\n"

    message = [{"role": "assistant", "content": prompt}]

    # Retry 3 times if timeout occurs
    for i in range(3):
        try:
            # completion = openai.ChatCompletion.create(
            #     engine="initial",
            #     messages=message,
            #     temperature=1.0,
            #     max_tokens=3000,
            #     top_p=0.95,
            #     frequency_penalty=0,
            #     presence_penalty=0,
            #     stop=None
            # )
            completion = openai.ChatCompletion.create(
            model= "gpt-3.5-turbo",
            messages= message,
            temperature= 1.0,# default values
            top_p= 1.0# default values
            )
            break
        except openai.exceptions.RequestTimeoutError:
            if i < 2:  # Retry attempts
                print("Timeout occurred. Retrying...")
                time.sleep(30)
            else:
                print("Max retries exceeded.")

    response = completion.choices[0].message["content"]
    questions = parse_response(response)

    qa_pairs = []
    for question in questions:
        message = [{"role": "assistant", "content": question}]
        
        # Retry 3 times if timeout occurs
        for i in range(3):
            try:
                # completion = openai.ChatCompletion.create(
                #     engine="initial",
                #     messages=message,
                #     temperature=0.7,
                #     max_tokens=2000,
                #     top_p=0.95,
                #     frequency_penalty=0,
                #     presence_penalty=0,
                #     stop=None
                # )
                completion = openai.ChatCompletion.create(
                model= "gpt-3.5-turbo",
                messages= message,
                temperature= 1.0,# default values
                top_p= 1.0# default values
                )
                break
            except openai.exceptions.RequestTimeoutError:
                if i < 2:  # Retry attempts
                    print("Timeout occurred. Retrying...")
                    time.sleep(30)
                else:
                    print("Max retries exceeded.")
        
        answer = completion.choices[0].message["content"]
        qa_pairs.append({'question': question, 'answer': answer})

    lock.acquire()
    if response:
        generate_task[it] = {'指南': input_book, 'qa_pairs': qa_pairs}
        bar.next()
        with open(output_filepath, "w", encoding="utf-8") as f:
            json.dump(generate_task, f, indent=4, ensure_ascii=False)
    lock.release()


def main():
    global count
    count = 0

    print('Building threads')
    pool = ThreadPoolExecutor(max_workers=6)
    # The number of CPU cores multiplied by a factor (e.g., 2-4) to provide enough parallelism without overwhelming the system.
    # i5 8400 has 6 cores 6 threads, thus set worker number to 6.
    # thus set to 6 just to be safe.

    res = pool.map(gpt_generate, data_list)

    pool.shutdown()
    bar.finish()
    print('All data saved.')
    with open(output_filepath, "w", encoding="utf-8") as f:
        json.dump(generate_task, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
