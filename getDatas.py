from urllib.request import urlopen
import re
import requests
from bs4 import BeautifulSoup


# 获取所有许可证的链接以及名字
def get_license():
    # 包含所有许可证网站的内容解析
    html = urlopen("https://opensource.org/licenses/alphabetical").read().decode('utf-8')
    soup = BeautifulSoup(html, 'lxml')
    opensource_list = soup.find('div', class_='field-item even')
    li_list = opensource_list.find_all('li')
    for li in li_list:
        # 获取协议的链接信息
        license_href = 'https://opensource.org' + li.find('a')['href']
        license_name = li.text.replace('\n', '')
        reg = r'(.*)'
        license_name = re.findall(reg, license_name)[0]
        print(license_name + ":" + license_href)
        # 将各个协议写入文件
        with open("data/All_license_link.txt", 'a', encoding='utf-8') as f:
            f.write(license_name+ '\t' +license_href + "\n")
        # 由于有些协议名字中含有“/"或者‘”’，文件命名时不能识别，需要进行替换
        if license_name.find('/'):
            license_name = license_name.replace('/', ' ')
        if license_name.find('"'):
            license_name = license_name.replace('"', ' ')
        filename = license_name + '.txt'
        # 读取各个对应的协议的内容
        try:

            html = requests.get(license_href).text

        except requests.exceptions.ConnectionError:

            requests.status_code = "Connection refused"



        soup = BeautifulSoup(html, 'lxml')
        container = soup.find('div', class_='field-item even')
        # 由于某些协议文本显示内容中有不相关的信息，所以需要就行内容的筛选
        all_href = container.find_all('p')
        s = ""
        s1 = ""
        for l in all_href:
            s += l.get_text() + "\n"
            s = s.lower()
        all_href1 = container.find_all('pre')
        if all_href1 == None:
            pass
        else:
            for l1 in all_href1:
                s1 += l1.get_text() + "\n"
                s1 = s1.lower()
        content = s + s1

        # 将各个协议写入文件
        with open("licensefile/" + filename, 'w+', encoding='utf-8') as f:
            f.write(soup.h1.get_text() + "\n\n\n" + content)


if __name__ == '__main__':
    get_license()