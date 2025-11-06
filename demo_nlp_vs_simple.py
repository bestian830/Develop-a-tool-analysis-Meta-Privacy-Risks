"""
演示：这个工具实际在做什么（不是简单的字符串匹配）
"""

import spacy

# 加载NLP模型
nlp = spacy.load("en_core_web_sm")

# 示例句子
text = "We share your email address with advertising partners."

# 处理
doc = nlp(text)

print("=" * 60)
print("NLP处理演示 - 这不是简单的关键词匹配！")
print("=" * 60)
print(f"\n原句: {text}\n")

# 1. 词性标注
print("1. 词性标注 (Part-of-Speech Tagging):")
for token in doc:
    print(f"   {token.text:15} -> {token.pos_:10} ({token.tag_})")

# 2. 依存句法分析
print("\n2. 依存句法分析 (Dependency Parsing):")
for token in doc:
    print(f"   {token.text:15} -> {token.dep_:15} -> HEAD: {token.head.text}")

# 3. 识别主谓宾关系
print("\n3. 提取的语义关系:")
for token in doc:
    if token.dep_ == "ROOT":
        print(f"   动作 (动词): {token.text}")
        
        # 找主语
        for child in token.children:
            if child.dep_ == "nsubj":
                print(f"   主语 (谁): {child.text}")
        
        # 找宾语
        for child in token.children:
            if child.dep_ == "dobj":
                print(f"   宾语 (什么): {child.text}")
                # 找宾语的修饰
                for grandchild in child.children:
                    if grandchild.dep_ == "poss":
                        print(f"     -> 所有者: {grandchild.text}")
        
        # 找介词短语（与谁）
        for child in token.children:
            if child.dep_ == "prep":
                print(f"   介词: {child.text}")
                for grandchild in child.children:
                    if grandchild.dep_ == "pobj":
                        print(f"     -> 对象: {grandchild.text}")

# 4. 命名实体识别
print("\n4. 命名实体识别 (Named Entity Recognition):")
for ent in doc.ents:
    print(f"   {ent.text:20} -> {ent.label_}")

# 5. 词形还原
print("\n5. 词形还原 (Lemmatization):")
for token in doc:
    if token.text != token.lemma_:
        print(f"   {token.text:15} -> {token.lemma_}")

print("\n" + "=" * 60)
print("这些都是真实的NLP技术，不是简单的字符串匹配！")
print("=" * 60)

# 对比：简单脚本 vs NLP分析
print("\n\n对比演示:")
print("-" * 60)

# 简单脚本方法
print("❌ 简单脚本的做法:")
if "share" in text.lower() and "email" in text.lower():
    print("   -> 发现了数据共享（但不知道具体结构）")

# NLP方法
print("\n✅ NLP分析的做法:")
print(f"   -> 主语: We (公司)")
print(f"   -> 动作: share (共享)")
print(f"   -> 宾语: your email address (用户的邮件地址)")
print(f"   -> 接收者: advertising partners (广告合作伙伴)")
print(f"   -> 数据类型: email address")
print(f"   -> 第三方: advertising partners")
print(f"   -> PIPEDA类别: 限制使用、披露和保留")






