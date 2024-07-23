import os

import requests
from bs4 import BeautifulSoup
import duckdb
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

con = duckdb.connect("theory.db")
# con.execute(
#     "CREATE OR REPLACE TABLE Questions (Rowid int, Question VARCHAR, Answer1 VARCHAR, Answer1_value bool, Answer2 VARCHAR, Answer2_value bool, Answer3 VARCHAR, Answer3_value bool, Answer4 VARCHAR, Answer4_value bool, Image VARCHAR, Correct bool, Type VARCHAR);"
# )
# url = "http://teo.co.il/questions/c1/"
url = "http://teo.co.il"


def get_list(url):
    page = requests.get(url, verify=False)
    soup = BeautifulSoup(page.content, "html.parser")
    result = soup.find("li", {"data-menu": "/questions"})
    types = result.find_all("li")
    type_list = {}
    for type in types:
        clean_type = re.search("\(([^)]+)", type.string).group(1)
        type_list[clean_type] = type.a["href"]
    return type_list


def num_questions(type_url):
    page = requests.get(type_url, verify=False)
    soup = BeautifulSoup(page.content, "html.parser")
    result = soup.find("ol")
    qs = len(result.find_all("li"))
    return qs


def reload(type, type_url):
    path = f"Images\{type}"
    if not os.path.exists(path):
        os.makedirs(path)
    for i in range(1, num_questions(type_url)):

        page = requests.get(type_url + "/" + str(i), verify=False)
        #  print(page.text)
        soup = BeautifulSoup(page.content, "html.parser")

        results = soup.find(id="questions")
        question = results.find("span", class_="question-self")

        # print(results)
        q = question.text.replace("'", "''")
        # print(f"Question: {q}")

        answers = {}
        for elements in results.select("label"):
            # print(elements["style"])
            if elements["style"] == "":
                correct = 0
            else:
                correct = 1
            answers[elements.text.replace("'", "''")] = correct

        # print(answers)
        imgname = ""
        for elements in results.select("img"):
            # print(elements["src"])
            img_data = requests.get(elements["src"], verify=False).content
            imgname = f"{path}\img_{str(i)}.jpg"
            with open(imgname, "wb") as handler:
                handler.write(img_data)

        query = f"Insert into Questions values ({i},'{q}'"

        for x, y in answers.items():
            query = query + f", '{x}', {y}"
        query = query + f", '{imgname}', False, '{type}')"
        print(query)
        con.sql(query)

        print(i)


# reload("a3", "https://teo.co.il/questions/a3")
# print(get_list(url).keys())
