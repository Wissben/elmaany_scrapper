import bs4 as soup
import nltk
import pprint
import pyarabic.araby as araby
import json
from selenium import webdriver


nltk.data.path.append("/media/weiss/Data/nltk_data")
file = open("dico.json",'r')
data = json.load(file)
pprint.pprint(len(data))

option = webdriver.ChromeOptions()
option.add_argument("- incognito")
# option.add_argument("--no-startup-window")
browser = webdriver.Chrome(executable_path="/home/weiss/Tools/chromedriver", chrome_options=option)


def name_exists(dic,name):
    for k in dic:
        if(k==name):
            return True
    return False

def postag_exists(dic,postag):
    for k in dic:
        if(k==postag):
            return True
    return False

def update_entry(dic,entry):
    name = entry['name']
    if(name_exists(dic,name)):
        if(postag_exists(dic[name],entry['posTag'])):
            dic[name][entry['posTag']] = dic[name][entry['posTag']] + entry['defs']
            dic[name][entry['posTag']] =list(set(dic[name][entry['posTag']]))
        else:
            dic[name][entry['posTag']]=list(set(entry['defs']))
    else:
        dic[name]={entry['posTag']:entry['defs']}

def writeToJSONFile(path, fileName, data):

    filePathNameWExt = './' + path + '/' + fileName + '.json'
    with open(filePathNameWExt, 'w',encoding='utf8') as fp:
        json.dump(data, fp,indent=6,ensure_ascii=False)
        fp.close()

def read_file(path):
    f = open(path,"r")
    return f.readlines()

def make_request(url):
    # res = requests.get(url,headers={'User-Agent': 'Mozilla/5.0'})
    # res.raise_for_status()
    browser.get(url)
    return browser.page_source

def get_entries_from_page(page):
    url = "https://www.almaany.com/appendix.php?page="+str(page)+"&language=arabic&category=%D8%A7%D9%84%D9%85%D8%B9%D8%AC%D9%85%20%D8%A7%D9%84%D9%88%D8%B3%D9%8A%D8%B7&lang_name=%D8%B9%D8%B1%D8%A8%D9%8A"
    ret = []
    res = make_request(url)
    souped = soup.BeautifulSoup(res,features="html5lib")
    table = souped.find("div", {'class':'row','id':'page-content'}).find("tbody", recursive=True)#.find("table", recursive=False)
    entries = table.findAll("a",recursive=True)
    ret = [soup.BeautifulSoup(str(entry),features='html5lib').text for entry in entries]
    return ret





def get_definitions_from_entry(entry,meaning_count=5):
    url = "https://www.almaany.com/ar/dict/ar-ar/"+entry+"/"
    res = make_request(url)
    souped = soup.BeautifulSoup(res, features="html5lib")
    alternatives = souped.find("ol",{"class","meaning-results"},recursive=True).findAll('li',recursive=False)# .find("table", recursive=False)
    for alternative in alternatives :
        means = get_meanings_from_alternative(alternative)
        name_postag = get_pos_tag_from_entry(alternative)
        if(name_postag is not None):
            obj = {'name': name_postag[0], 'posTag': name_postag[1], 'defs': means}
            update_entry(data,obj)

def get_meanings_from_alternative(alternative):
    alt = str(alternative)
    souped = soup.BeautifulSoup(alt, features="html5lib")
    lis = souped.find('ul',recursive=True).findAll('li',recursive=False)
    return ([ x.text for x in lis])

def get_pos_tag_from_entry(entry):
    meanings_souped = soup.BeautifulSoup(str(entry), features='html5lib')
    name = meanings_souped.find('span')
    pos = meanings_souped.find('span').next_sibling
    ha = nltk.re.findall("\((.+?)\)", pos)
    if(not ha):
        return None
    return (araby.strip_tashkeel(name.text),ha[0])



def save_page_to_hmtl(ent):
    res = make_request("https://www.almaany.com/ar/dict/ar-ar/"+ent+"/")
    with open("./Pages/"+ent+'.htm','w') as f:
        f.write(res)
        f.close()


total_pages = 25
for page in range(1,total_pages):
    print("GETTING WORDS FROM PAGE %d / %d "%(page,total_pages))
    ents = get_entries_from_page(page)
    print("GOT WORDS FROM PAGE %d"%(page))
    # pprint.pprint(ents)
    start = 0
    total = 50 #int(len(ents)*0.1)
    for i in range(start,total):
        if(len(str(ents[i]))>2):
            # save_page_to_hmtl(str(ents[i]))
            # print('DOWNLOADED PAGE %d / %d' %(i,total))
            print('\t\tSCRAPPING %s :  %d / %d ...' %(str(ents[i]),i,total))
            ret = get_definitions_from_entry(str(ents[i]))
            print('\t\tSCRAPPED : ', ents[i])
    writeToJSONFile('./', 'dico', data)

# total_pages = 201
# for page in range(1,total_pages):
#     print("GETTING WORDS FROM PAGE %d / %d "%(page,total_pages))
#     ents = get_entries_from_page(page)
#     print("GOT WORDS FROM PAGE %d"%(page))
#     # pprint.pprint(ents)
#     start = 0
#     total = int(len(ents)*0.1)
#     for i in range(start,total):
#         if(len(str(ents[i]))>2):
#             # save_page_to_hmtl(str(ents[i]))
#             # print('DOWNLOADED PAGE %d / %d' %(i,total))
#             print('\t\tSCRAPPING %s :  %d / %d ...' %(str(ents[i]),i,total))
#             ret = get_definitions_from_entry(str(ents[i]))
#             print('\t\tSCRAPPED : ', ents[i])


# ents = get_entries_from_page(1)
# ents = ['الجَدْي',
#  'آذان الحيطان',
#  'آذان الدُّبّ',
#  'آذان الشاة',]
# pprint.pprint(ents)
# for ent in ents:
#     get_definitions_from_entry(ent)
# # # get_definitions_from_entry(entry='آذان')
#
