# LLM-playground

随便玩玩LLM相关的预处理。站在了很多之前巨人的肩膀上，向他们表示感谢！

# Step 0 data collection

略，各种方法去找需要的电子书PDF。

# Step 1 OCR tricks

使用了若干OCR工具，包括WPS，[福昕](www.pdf365.cn)，Paddle等。发现如果一整本(500页的样子)喂进去会导致无法辨认，会直接把页面截图返回给我。所以先用福昕去水印，然后将范围缩减到正文开始，去掉前后的封面目录等信息。得到docx文件，此时也包括了图片等。

# Step 2 pre-processing

这一步将word文件清洗后另存为txt格式（utf-8）。使用step2.py。

```
python step2.py --input_folder D:/Desktop/注册安全工程师/处理过程 --output_folder D:/Desktop/注册安全工程师/处理过程 --max_chars 500
```
This code does following:
- Removes headers and footers from DOCX files
- Cleans text by removing unnecessary characters, spaces, and Chinese punctuation marks
- Combines sentences to create lines with a specified maximum number of characters (default: 500)
- Saves cleaned text to TXT files and a JSON file

注意这里是按句子分行的，但是有的句子特别短，参考医学教科书，有两种切分形式，且教科书的结果很干净，所以并不需要像webcrawl的内容一样的清洗策略。所以这里我们限制使多个句子合并成一个，每行的字数控制在200字的样子。当然了这里还有很多工作可以做。

原始文件355页18M，得到txt，6844行35万字。样例数据：

<ul>
第一章机械安全技术
第一节机械安全基础知识
　　　机械设备无处不在、无时不用，是人类进行生产经营活动不可或缺的重要工具。现代 机械科技含量高，是机、电、光、液等多种技术集成的复杂系统。机械在减轻劳动强度给 人们带来高效、方便的同时，也带来了不安全因素。任何机械在进行生产或服务活动时都 伴随着安全风险，机械安全问题越来越受到人们的重视。
一、	机械基本概念
　　　机械是由若干个零、部件连接构成，其中至少有一个零、部件是可运动的，并且配备 或预定配备动力系统，是具有特定应用目的的组合。机械包括：
　　　(1)单台的机械。例如，木材加工机械、金属切削机床、起重机等。
　　　(2)实现完整功能的机
</ul>


这个数据有三个用处，用来预训练，用来生成SFT，用来算embedding进行检索。过程参考了5月25号笔记的测试。
OCR后的文字有1.化工教材_wpsocr 47万字。2.技术教材_wpsocr 30万字。3.法规教材_wpsocr 62万字。4.管理教材_wpsocr 32万字。最终形成的lines.json一共160万字。

# Step 3 生成SFT

这部分的目的是生成与领域相关的SFT对.

## Book based QA generation
目的是根据给定的语料去生成若干问题，参考了上海交大中文医疗对话语言模型的生成方式 (https://github.com/MediaBrain-SJTU/MedicalGPT-zh)。通过提供教科书文本，先让ChatGPT生成与该段教科书知识内容相关的若干问题，再通过“文本段-问题”对的方式让ChatGPT回答问题，从而能够生成knowledge grounded instructions。

使用时请注意，将代码中的'YOUR_API_KEY'替换为您实际的OpenAI API密钥。如果您有多个密钥，请将它们添加到代码中的api_keys列表中以加快数据生成速度。将书籍材料放入JSON文件中，参考文件见`原材料.json`。输入输出的文件地址写死了。

生成的问答对将保存在book_based_qa.json文件中。作为参考，max_worker=6，12小时2000条。


## GPT based QA generation

参考了BELLE 1.5M SFT生成方式(https://github.com/LianjiaTech/BELLE/tree/main/data/1.5M)。生成格式是：

```json
instruction: 指令
input: 输入
output: 输出
```

但是我们认为这个方法生成出的结果，虽然能够保证快速大量和diverse的输出，但是不够深入，所以这个方法没有沿用。使用的是`gpt-3.5-turbo`模型，命令：

```bash
# install requirements
python generate_instruction.py generate_instruction_following_data --api=chat --model_name=gpt-3.5-turbo --num_instructions_to_generate 10000
```

我们给出了一个样例输出文件`化工sft-小.json`。
