from flask import Flask, request, render_template, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import spacy
from deep_translator import GoogleTranslator
import re
import os
import random

app = Flask(__name__)

# 配置ChromeDriver路径
CHROMEDRIVER_PATH = r"C:\Users\SZ0201\Desktop\chromedriver-win64\chromedriver.exe"
nlp = spacy.load("en_core_web_sm")

def extract_text_from_tweet(url):
    # 验证URL格式
    if not re.match(r'https?://(x\.com|twitter\.com)/\S+', url):
        return None
        
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--log-level=3')
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        time.sleep(5)
        element = driver.find_element(By.CSS_SELECTOR, 'article div[lang]')
        return element.text.strip()
    except Exception as e:
        print("抓取失败：", e)
        return None
    finally:
        driver.quit()

def translate_text(text):
    try:
        # 长文本处理
        if len(text) > 5000:
            text = text[:5000] + "... [内容过长已截断]"
        return GoogleTranslator(source='auto', target='zh-CN').translate(text)
    except Exception as e:
        print(f"翻译失败: {e}")
        return "翻译失败"

def extract_keywords(text):
    """改进关键词提取算法"""
    doc = nlp(text)
    
    # 提取名词短语和实体
    keywords = set()
    noun_phrases = [chunk.text for chunk in doc.noun_chunks]
    entities = [ent.text for ent in doc.ents if ent.label_ in ['PERSON', 'ORG', 'GPE', 'PRODUCT', 'EVENT']]
    
    # 添加重要词性
    important_tokens = [
        token.text for token in doc 
        if token.pos_ in ['NOUN', 'PROPN', 'ADJ', 'VERB'] 
        and not token.is_stop 
        and len(token.text) > 2
    ]
    
    keywords.update(noun_phrases)
    keywords.update(entities)
    keywords.update(important_tokens)
    
    # 按频率和长度排序
    return sorted(keywords, key=lambda x: (text.count(x), len(x)), reverse=True)[:10]

def extract_attractive_content(text):
    """识别吸引用户的内容"""
    doc = nlp(text)
    attractive_elements = []
    
    # 1. 提取情感强烈的句子
    emotional_sentences = [
        sent.text.strip() for sent in doc.sents 
        if any(token.text in ['!', '?'] for token in sent)
    ]
    
    # 2. 提取问题和呼吁行动
    action_phrases = [
        sent.text.strip() for sent in doc.sents 
        if any(token.text.lower() in ['how', 'why', 'what', 'should', 'must'] for token in sent)
    ]
    
    # 3. 提取数字和统计数据
    number_phrases = [
        chunk.text for chunk in doc.noun_chunks 
        if any(token.like_num for token in chunk)
    ]
    
    # 4. 提取专有名词和热门话题
    trending_topics = [
        ent.text for ent in doc.ents 
        if ent.label_ in ['PERSON', 'ORG', 'PRODUCT', 'EVENT']
    ]
    
    # 组合所有吸引元素
    attractive_elements.extend(emotional_sentences[:2])
    attractive_elements.extend(action_phrases[:1])
    attractive_elements.extend(number_phrases[:2])
    attractive_elements.extend(trending_topics[:3])
    
    # 去重并按长度排序
    unique_elements = list(set(attractive_elements))
    return sorted(unique_elements, key=len, reverse=True)[:3]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_tweet():
    data = request.get_json()
    tweet_url = data.get('tweet_url')
    
    if not tweet_url:
        return jsonify({"error": "缺少推文链接"}), 400
        
    # 提取推文内容
    tweet_content = extract_text_from_tweet(tweet_url)
    
    if not tweet_content:
        return jsonify({"error": "无法获取推文内容"}), 500
        
    # 翻译文本
    translation = translate_text(tweet_content)
    
    # 提取关键词
    keywords = extract_keywords(tweet_content)
    
    # 提取吸引内容
    attractive_content = extract_attractive_content(tweet_content)
    
    return jsonify({
        "success": True,
        "tweet_content": tweet_content,
        "translation": translation,
        "keywords": keywords,
        "attractive_content": attractive_content
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5491)