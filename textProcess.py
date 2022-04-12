import re
import nltk
import os
import xlwt
import pandas as pd
from fuzzywuzzy import fuzz, process
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import string
import gensim
from gensim import corpora
from gensim.models import CoherenceModel
import xlsxwriter

# 利用re将license分句
def rePretreatment():
    with open("licensefile/0-clause BSD license.txt", "r") as f:  # 打开文件
        text = f.read()  # 读取文件
    text = text.replace('\n','')

    sentences = re.split('(。|！|\!|\.|？|\?)', text)

    print(sentences)

    return sentences

# 利用nltk将license分句
def nltkPretreatment(filePath):
    with open(filePath, "r", encoding='utf-8') as f:  # 打开文件
        text = f.read()  # 读取文件

    # 加载punkt句子分割器
    sen_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    # 对句子进行分割
    sentences = sen_tokenizer.tokenize(text)

    return sentences

def getAllTxtFiles():
    path = "licensefile/"
    files = os.listdir(path)
    return files

# 将所有license分句，并存储到excel表格中
def setAllLicenseSentenceExcel():
    # 创建工作簿
    f = xlwt.Workbook()

    # 创建一个sheet
    sheet = f.add_sheet('licenseSentences', cell_overwrite_ok=True)

    files = getAllTxtFiles()

    sheet.write(0, 0, 'license')
    sheet.write(0, 1, 'sentence')
    rowNum = 1
    for filename in files:
        filePath = 'licensefile/'+filename
        sentences = nltkPretreatment(filePath)
        for sentence in sentences:
            sentence = sentence.replace('\n', '')
            sheet.write(rowNum, 0, filename.replace('.txt', ''))
            sheet.write(rowNum, 1, sentence)
            rowNum = rowNum + 1

    f.save('licenseData.xls')

# 得出两个句子的相似度
def getSimilarity(sentence1, sentence2):
    return fuzz.partial_ratio(sentence1, sentence2)

def getExcelSentence():
    sheet = pd.read_excel("licenseData.xls", "licenseSentences")
    sentenceList = []
    for row in sheet.index.values:
        doc = dict()
        doc['license'] = sheet.iloc[row, 0]
        doc['sentence'] = sheet.iloc[row, 1]

        sentenceList.append(doc)
    return sentenceList
def getSentenceList():
    data = pd.read_excel('licenseData.xls', sheet_name='licenseSentences')
    df = pd.DataFrame(data)
    sentences = list(df['sentence'])
    return sentences

def getLicenseList():
    data = pd.read_excel('licenseData.xls', sheet_name='licenseSentences')
    df = pd.DataFrame(data)
    licenses = list(df['license'])
    return licenses

# 数据清洗和预处理
stop = set(stopwords.words('english'))
exclude = set(string.punctuation)
lemma = WordNetLemmatizer()

def clean(doc):
    stop_free = " ".join([i for i in doc.lower().split() if i not in stop])
    punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
    normalized = " ".join(lemma.lemmatize(word) for word in punc_free.split())
    return normalized


# 构建 LDA 模型
def createLDAModel(doc_complete):
    doc_clean = [clean(doc).split() for doc in doc_complete]

    # # 创建语料的词语词典，每个单独的词语都会被赋予一个索引
    # dictionary = corpora.Dictionary(doc_clean)
    #
    # # 使用上面的词典，将转换文档列表（语料）变成 DT 矩阵
    # doc_term_matrix = [dictionary.doc2bow(doc) for doc in doc_clean]
    #
    # # 使用 gensim 来创建 LDA 模型对象
    # Lda = gensim.models.ldamodel.LdaModel
    #
    # # 在 DT 矩阵上运行和训练 LDA 模型
    # ldamodel = Lda(doc_term_matrix, num_topics=250, id2word=dictionary, passes=50)

    id2word = corpora.Dictionary(doc_clean)  # Create Dictionary
    corpus = [id2word.doc2bow(text) for text in doc_clean]  # Term Document Frequency

    # Build LDA model
    lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                                id2word=id2word,
                                                num_topics=250,
                                                random_state=100,
                                                update_every=1,
                                                chunksize=100,
                                                passes=10,
                                                alpha='auto',
                                                per_word_topics=True)

    # 输出结果
    print('coherence_score:', getCoherenceScore(lda_model, doc_clean, id2word))

    return lda_model

# 构造mallet主题模型
def createMalletModel(doc_complete):
    doc_clean = [clean(doc).split() for doc in doc_complete]
    id2word = corpora.Dictionary(doc_clean)  # Create Dictionary
    corpus = [id2word.doc2bow(text) for text in doc_clean]  # Term Document Frequency

    base_path = os.path.dirname(__file__)
    mallet_path = os.path.join(base_path, 'tool', 'mallet-2.0.8', "bin", "mallet")
    os.environ['MALLET_HOME'] = os.path.join(base_path, 'tool', 'mallet-2.0.8')

    ldamallet = gensim.models.wrappers.LdaMallet(mallet_path, corpus=corpus, num_topics=250, id2word=id2word)

    print('\nCoherence Score: ', getCoherenceScore(ldamallet, doc_clean, id2word))
    return ldamallet

# 得到LDA模型的Coherence Score
def getCoherenceScore(model, texts, dictionary):
    coherence_model_ldamallet = CoherenceModel(model=model, texts=texts, dictionary=dictionary,
                                               coherence='c_v')
    coherence_score = coherence_model_ldamallet.get_coherence()
    return coherence_score

def compute_coherence_values(dictionary, corpus, texts, limit, start=2, step=3):
    """
    Compute c_v coherence for various number of topics

    Parameters:
    ----------
    dictionary : Gensim dictionary
    corpus : Gensim corpus
    texts : List of input texts
    limit : Max num of topics

    Returns:
    -------
    model_list : List of LDA topic models
    coherence_values : Coherence values corresponding to the LDA model with respective number of topics
    """
    base_path = os.path.dirname(__file__)
    mallet_path = os.path.join(base_path, 'tool', 'mallet-2.0.8', "bin", "mallet")
    os.environ['MALLET_HOME'] = os.path.join(base_path, 'tool', 'mallet-2.0.8')

    coherence_values = []
    model_list = []
    for num_topics in range(start, limit, step):
        model = gensim.models.wrappers.LdaMallet(mallet_path, corpus=corpus, num_topics=250, id2word=dictionary)
        model_list.append(model)
        coherencemodel = CoherenceModel(model=model, texts=texts, dictionary=dictionary, coherence='c_v')
        coherence_values.append(coherencemodel.get_coherence())

    return model_list, coherence_values

def selectBestMalletModel(model_list, coherence_values):
    # Select the model and print the topics
    index = coherence_values.index(max(coherence_values))
    optimal_model = model_list[index]

    return optimal_model

def format_topics_sentences(ldamodel, corpus, texts):
    # Init output
    sent_topics_df = pd.DataFrame()

    # Get main topic in each document
    for i, row in enumerate(ldamodel[corpus]):
        row = sorted(row, key=lambda x: (x[1]), reverse=True)
        # Get the Dominant topic, Perc Contribution and Keywords for each document
        for j, (topic_num, prop_topic) in enumerate(row):
            if j == 0:  # => dominant topic
                wp = ldamodel.show_topic(topic_num)
                topic_keywords = ", ".join([word for word, prop in wp])
                sent_topics_df = sent_topics_df.append(pd.Series([int(topic_num), round(prop_topic,4), topic_keywords]), ignore_index=True)
            else:
                break

    sent_topics_df.columns = ['Dominant_Topic', 'Perc_Contribution', 'Topic_Keywords']



    # Add original text to the end of the output
    contents = pd.Series(texts)
    sent_topics_df = pd.concat([sent_topics_df, contents], axis=1)
    return(sent_topics_df)


# license分句后，构建LDA模型，并将训练结果存到Excel
def LDAresult():


    sentences = getSentenceList()
    doc_clean = [clean(doc).split() for doc in sentences]
    id2word = corpora.Dictionary(doc_clean)  # Create Dictionary
    corpus = [id2word.doc2bow(text) for text in doc_clean]  # Term Document Frequency

    model_list, coherence_values = compute_coherence_values(dictionary=id2word, corpus=corpus, texts=doc_clean, start=5, limit=30, step=5)
    mallet_model = selectBestMalletModel(model_list, coherence_values)

    print(mallet_model.print_topics())
    print('\nCoherence Score: ', getCoherenceScore(mallet_model, doc_clean, id2word))

    df_topic_sents_keywords = format_topics_sentences(ldamodel=mallet_model, corpus=corpus, texts=doc_clean)

    # Format
    df_dominant_topic = df_topic_sents_keywords.reset_index()
    df_dominant_topic.columns = ['Document_No', 'Dominant_Topic', 'Topic_Perc_Contrib', 'Keywords', 'Text']
    licenselist = getLicenseList()
    df_dominant_topic.insert(0, 'License', licenselist)

    # # Show
    # # 显示所有列
    # pd.set_option('display.max_columns', None)
    # # 显示所有行
    # pd.set_option('display.max_rows', None)
    # # 设置value的显示长度为100，默认为50
    # pd.set_option('max_colwidth', 100)
    #
    # print(df_dominant_topic)

    # create a Pandas Excel writer using xlswriter

    writer = pd.ExcelWriter('data/result_250topics.xlsx', engine='xlsxwriter', options={'strings_to_urls':False})

    df_dominant_topic.to_excel(writer, sheet_name='Data', startcol=0, index=False)

    writer.save()




if __name__ == '__main__':

    LDAresult()