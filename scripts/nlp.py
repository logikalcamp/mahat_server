import requests
import spacy
import re
from datetime import datetime
from utils import datesHeb,dates

spam_words = ['מאת:','נשלח:','טל:','From:','Sent:','To:','To:','אל:','Subject:','____________','נשלח מה-Galaxy','-------- הודעה מקורית --------',]
spam_emails = ['ט.ל.ח','מבצע סוף שנה','חברי מועדון','גמר המלאי','לכניסה ראשונה','Microsoft','מישור החוף','קיבלנו את פנייתך','שיתף/ה איתך קובץ','The Monthly Standup','You have been invited','Join with Google Meet']
platforms = ["monday","trello","zendesk","jira","asana"]

nlp = spacy.load("en_core_web_sm")


def checkHeb(exp):
    chars = ['א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט', 'י', 'כ', 'ל', 'מ', 'נ', 'ס', 'ע', 'פ', 'צ', 'ק', 'ר', 'ש',
             'ת', 'ם', 'ן', 'ף', 'ץ', 'ך']
    counter = 0
    for i in exp:
        print(i in chars)
        if i in chars:
            counter += 1
    print(counter)
    if (counter > len(exp) / 2):
        return True
    else:
        return False

def check_if_cta(text,user,assignees,email):
    isSpam = False
    for k in spam_emails:
        if k in text:
            isSpam = True
    if not isSpam:
        broke = text.splitlines()

        for b in broke:
            for sw in spam_words:
                if sw in b:
                    # print(b)
                    text = text.replace(b,'')
        if (text.strip() != ''):
            if(checkHeb(text)):
                request = {
                    'token': 'xffluaDuOpmmbAG',
                    "readable": False,
                    'paragraph': text
                }
                result = requests.post('https://hebrew-nlp.co.il/service/Morphology/Analyze', json=request).json()
                for sent in result:
                    counter = 0
                    for word in sent:
                        if (word[0]["partOfSpeech"] == 'VERB' and word[0]["tense"] in ['FUTURE','INFINITIVE'] and word[0]["person"] != "FIRST" and word[0]["baseWord"] not in ['הודה']):
                            if counter != 0:
                                if sent[counter-1][0]["ownershipPerson"] == "NONE":
                                    print(True)
                                    if user["eng"] in text:
                                        return True,"english word in text"
                                    if user["heb"] in text:
                                        return True,"hebrew word in text"
                                    # if len(assignees) == 2 and email in assignees:
                                    #     return True,"personal email"
                            else:
                                if user["eng"] in text:
                                    return True,"english word in text"
                                if user["heb"] in text:
                                    return True,"hebrew word in text"
                                # if len(assignees) == 2 and email in assignees:
                                #     return True,"personal email"
                        counter += 1
            else:
                newExp = text.replace(' has to ', ' should ')
                newExp = newExp.replace(' have to ', ' should ')
                current = nlp(newExp)

                counter = 0
                sec = 0
                for word in current:
                    if (word.pos_ == 'VERB' and word.tag_ in ['VB', 'VBG', 'VBZ'] and word.dep_ in ['ROOT', 'acl',
                                                                                                    'compound',
                                                                                                    'amod', 'relcl',
                                                                                                    'acomp',
                                                                                                    'advcl', 'relcl'] and user["eng"] in text):
                        return True, "there is verb"
        # if len(assignees) == 2 and email in assignees and "?" in text:
        #     return True,"personal name with question"

    return False,"nothing"

def checkRegex(val):
    response = {
        "date":'',
        "exp":''
    }
    regexExtendFormats = [
        {
            "re":r"\d{2}-\d{2}",
            'da':'%d-%m'
        },
        {
            "re": r"\d{2}-\d{2}",
            'da': '%m-%d'
        },
        {
            "re":r"\d{2}-\d{2}-\d{2}",
            "da":'%d-%m-%y'
        },
        {
            "re": r"\d{2}-\d{2}-\d{2}",
            "da": '%m-%d-%y'
        },
        {
            "re":r"\d{2}-\d{2}-\d{4}",
            "da":'%d-%m-%y'
        },
        {
            "re":r"\d{2}-\d{2}-\d{4}",
            "da":'%m-%d-%y'
        },
        {
            "re":r"\d{4}-\d{2}-\d{2}",
            "da":'%y-%m-%d'
        },
        {
            "re":r"\d{4}-\d{2}-\d{2}",
            "da":'%y-%d-%m'
        },
        {
            "re":r"\d{2}/\d{2}",
            "da":'%m/%d'
        },
        {
            "re":r"\d{2}/\d{2}",
            "da":'%d/%m'
        },{
            "re":r"\d{2}/\d{2}/\d{2}",
            "da":'%d/%m/%y'
        },
        {
            "re": r"\d{2}/\d{2}/\d{2}",
            "da": '%m/%d/%y'
        },
        {
            "re":r"\d{2}/\d{2}/\d{4}",
            "da":'%d/%m/%y'
        },
        {
            "re":r"\d{2}/\d{2}/\d{4}",
            "da":'%m/%d/%y'
        },
        {
            "re":r"\d{4}/\d{2}/\d{2}",
            "da":'%y/%m/%d'
        },
        {
            "re":r"\d{4}/\d{2}/\d{2}",
            "da":'%y/%d/%m'
        },
    #
        {
            "re": r"\d{2}.\d{2}",
            "da": '%m.%d'
        },
        {
            "re": r"\d{2}.\d{2}",
            "da": '%d.%m'
        }, {
            "re": r"\d{2}.\d{2}.\d{2}",
            "da": '%d.%m.%y'
        },
        {
            "re": r"\d{2}.\d{2}.\d{2}",
            "da": '%m.%d.%y'
        },
        {
            "re": r"\d{2}.\d{2}.\d{4}",
            "da": '%d.%m.%y'
        },
        {
            "re": r"\d{2}.\d{2}.\d{4}",
            "da": '%m.%d.%y'
        },
        {
            "re": r"\d{4}.\d{2}.\d{2}",
            "da": '%y.%m.%d'
        },
        {
            "re": r"\d{4}.\d{2}.\d{2}",
            "da": '%y.%d.%m'
        },{
            "re":r"\d{1}.\d{1}",
            "da":'%d.%m'
        },{
            "re":r"\d{1}.\d{1}",
            "da":'%m.%d'
        },{
            "re":r"\d{1}/\d{1}",
            "da":'%d/%m'
        },{
            "re":r"\d{1}/\d{1}",
            "da":'%m/%d'
        },{
            "re":r"\d{1}-\d{1}",
            "da":'%d-%m'
        },{
            "re":r"\d{1}-\d{1}",
            "da":'%m-%d'
        }
    ]
    for form in regexExtendFormats:
        potential = re.search(form["re"],val)
        # print(form)

        # if potential not None
        # date = datetime.datetime.strptime(potential.group(), '%Y-%m-%d').date()
        if potential != None:
            try:
                date = datetime.strptime(potential.group(), form["da"])
                print(date)
                if(date.year==1900):
                    date =  ''
                # print(form)
                response["date"] = date
                response["exp"] = potential.group()

            except ValueError as e:
                print("with error",form)
                print(e)
                pass

    return response

def set_due_dates(text):
    dueDate = ''
    if (checkHeb(text)):
        for i in datesHeb:
            for j in i["alt"]:
                if j in text:
                    deadline = j
                    dueDate = i["phrase"]
                    print("succeed",dueDate)
    else:
        for i in dates:
            for j in i["alt"]:
                if j in text:
                    deadline = j
                    dueDate = i["phrase"]
                    print("succeed",dueDate)
    if dueDate == '':
        date = checkRegex(text)
        dueDate = date["date"]
        print("succeed", dueDate)
    return dueDate
