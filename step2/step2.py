# 20230525 Created by Nuo with help of gpt-4
# 20230614 Improved regular expression
# Turn OCRed text books in docx, data cleaning, save as txt and json files

import os
import json
import docx2txt
import re
import argparse
import sys
from pathlib import Path
import logging
from docx import Document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_text(text):
    # Remove consecutive newlines and extra whitespaces
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s{2,}', ' ', text)

    # Remove multiple Chinese punctuation marks
    #text = re.sub(r'[！？，、；：“”‘’（）【】—…—《》「」『』【】〔〕]+', '', text)

    # Remove non-Chinese characters except English letters and digits
    #text = re.sub(r'[^\u4e00-\u9fffA-Za-z\d\s.]', '', text)
    
    return text

def combine_sentences(lines, max_chars=500):
    combined_lines = []
    current_line = ''
    
    for line in lines:
        words = line.split()
        for word in words:
            if len(current_line) + len(word) <= max_chars:
                current_line += word + ' '
            else:
                combined_lines.append(current_line)
                current_line = word + ' '
        
    if current_line:
        combined_lines.append(current_line)
    
    return combined_lines

def process_docx_files(input_folder, output_folder, max_chars=500):
    all_lines = []

    for file_path in input_folder.glob("*.docx"):
        try:
            # Load the document
            doc = Document(str(file_path))

            # Extract the main document content (excluding headers and footers)
            paragraphs = [paragraph.text for paragraph in doc.paragraphs]

            # Clean and format paragraphs
            cleaned_paragraphs = [clean_text(paragraph) for paragraph in paragraphs]

            # Combine paragraphs into lines with around 500 characters
            combined_lines = combine_sentences(cleaned_paragraphs, max_chars=max_chars)
            combined_text = '\n'.join(combined_lines)

            # Save cleaned text to txt file
            output_file_path = output_folder / (file_path.stem + ".txt")
            with output_file_path.open('w', encoding='utf-8') as output_file:
                output_file.write(combined_text)

            # Add cleaned lines to the list
            all_lines.extend(combined_lines)

        except Exception as e:
            logger.error(f"Error processing file '{file_path}': {e}")

    # Save lines to JSON file
    with (output_folder / 'lines.json').open('w', encoding='utf-8') as json_file:
        json.dump(all_lines, json_file, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description='NLP Text Data Preprocessing')
    parser.add_argument('--input_folder', type=Path,default='D:/Desktop/注册安全工程师/处理过程', help='Path to the input folder containing DOCX files')
    parser.add_argument('--output_folder', type=Path,default='D:/Desktop/注册安全工程师/处理过程', help='Path to the output folder')
    parser.add_argument('--max_chars', type=int, default=500, help='Maximum characters per line (default: 500)')
    args = parser.parse_args()

    input_folder = args.input_folder
    output_folder = args.output_folder
    max_chars = args.max_chars

    if not input_folder.is_dir():
        logger.error("Input folder does not exist.")
        sys.exit(1)

    if not output_folder.is_dir():
        output_folder.mkdir(parents=True)

    process_docx_files(input_folder, output_folder, max_chars=max_chars)

if __name__ == '__main__':
    main()