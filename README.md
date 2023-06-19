# ChuizhiGPT

![_239dc35c-edeb-41a8-9042-d8dd9971ef74](https://github.com/nuoma/LLM-playground/assets/9259412/a9de8665-bd8e-4bca-bb5c-e4324c213ef7)

随便玩玩LLM相关的预处理。站在了很多之前巨人的肩膀上，向他们表示感谢！

pip requirements was created using `pipreqs --encoding=utf-8 .` which may not be accurate

# Step 0. Data Collection AKA Awesome（住嘴

略，各种方法去找需要的电子书PDF。找了各种贩卖专业电子书的途径，定向搜寻的电子书，甚至买书然后tb寄书扫描。以下十几个我觉得泰裤辣的dataset：

[政务向文档](抖音笔尖耕耘)，
[MNBVC在hf上的分类](https://huggingface.co/datasets/liwu/MNBVC/viewer/gov_report/train?row=0)，
[Massive Never-ending BT Vast Chinese corpus超大规模中文语料集](https://mnbvc.253874.net/)，
[医疗电子书](https://github.com/jind11/MedQA/tree/master)，
[中国法律数据](https://github.com/pengxiao-song/awesome-chinese-legal-resources)

# Step 1. OCR Tricks

测试了若干工具，包括：WPS，[福昕](www.pdf365.cn)，PaddleOCR，科大讯飞OCR，[SmallPDF](https://smallpdf.com/cn/unlock-pdf)等。氪金吧。发现如果一整本(500页的样子)喂进去会导致无法辨认，会直接把页面截图返回给我。所以先用福昕去水印(关键)，然后将范围缩减到正文开始，去掉前后的封面目录等信息。得到docx文件，此时也包括了图片等，整体质量可以接受。如果大于100M无法处理的就用WPS每隔200页成一个独立文档。如果文档加密就用[这个](https://smallpdf.com/cn/unlock-pdf) 。



# Step 2. Pre-Processing

这一步将word文件清洗后另存为txt格式（utf-8）。使用step2.py。

```
python step2.py --input_folder D:/Desktop/注册安全工程师/处理过程 --output_folder D:/Desktop/注册安全工程师/处理过程 --max_chars 500
```
This code does following:
- Removes headers and footers from DOCX files
- Cleans text by removing unnecessary characters, spaces, and Chinese punctuation marks
- Combines sentences to create lines with a specified maximum number of characters (default: 500)
- Saves cleaned text to TXT files and a JSON file

注意这里是按句子分行的，但是有的句子特别短，参考医学教科书，有两种切分形式，且教科书的结果很干净，所以并不需要像web crawl的内容一样的清洗策略。所以这里我们限制使多个句子合并成一个，每行的字数控制在200字的样子。当然了这里还有很多工作可以做。过程参考了5月25号笔记的测试。

用来测试的教科书原始文件355页18M，得到txt，6844行35万字。OCR后的文字有：1.化工教材_wpsocr 47万字。2.技术教材_wpsocr 30万字。3.法规教材_wpsocr 62万字。4.管理教材_wpsocr 32万字。四个文件合并处理后一共160万字，我们提供一个最终文件的样例`lines.json`。


我这里的处理方法还有待商榷，尤其是对于标点符号和断句的处理。这个数据有三个用处：
1. 预训练
2. 生成SFT
3. 算embedding进行检索。




# Step 3. Domain SFT Generation

这部分的目的是生成与领域相关的SFT对。

## GPT based QA generation

参考了BELLE 1.5M SFT生成方式(https://github.com/LianjiaTech/BELLE/tree/main/data/1.5M)。但是我们认为这个方法生成出的结果，虽然能够保证快速大量和diverse的输出，但是不够深入，所以**这个方法没有采用**。使用的是`gpt-3.5-turbo`模型，命令：

```bash
# install requirements
python generate_instruction.py generate_instruction_following_data --api=chat --model_name=gpt-3.5-turbo --num_instructions_to_generate 10000
```

我们给出了一个样例输出文件`化工sft-小.json`。

## Book based QA generation
目的是根据给定的语料去生成若干问题，通过提供教科书文本，先让ChatGPT生成与该段教科书知识内容相关的若干问题，再通过“文本段-问题”对的方式让ChatGPT回答问题，从而能够生成knowledge grounded instructions。参考了上海交大中文医疗对话语言模型[MedicalGPT-zh](https://github.com/MediaBrain-SJTU/MedicalGPT-zh)
的生成方式。

使用时请注意，将代码中的'YOUR_API_KEY'替换为您实际的OpenAI API密钥。如果您有多个密钥，请将它们添加到代码中的api_keys列表中以加快数据生成速度。将书籍材料放入JSON文件中，参考文件见`原材料.json`。输入输出的文件地址写死了。生成的问答对将保存在book_based_qa.json文件中。作为参考，max_worker=6，12小时2000条，花费18刀。如果传github切记把自己的key删掉，否则很快就会被github扫出来，然后你的key就被封了要重新生成，别问我怎么知道的。

生成的若干json文件可以使用json2csv.py变成csv格式，这样方便于适配不同种类的instruction format.

# Step 4 ContinuePreTrain(CPT) 

这里需要考虑的事情太多了，不多bb先动手，训练方法参考了[ymcui](https://github.com/ymcui/Chinese-LLaMA-Alpaca/wiki)，基座模型采用了[ziya](https://huggingface.co/IDEA-CCNL/Ziya-LLaMA-13B-v1)。到底应该在基座模型上动手还是在sft过的，我母鸡啊。

## 小
### 小小

# Step 5 SFT

## Data considerations

首先是

另一部分是领域相关的。作为测试，我们目前为止一共有，使用了专业词典保证广度，使用了专业考试保证专业度。

训练的顺序

关于instruction的格式

## Training considerations


