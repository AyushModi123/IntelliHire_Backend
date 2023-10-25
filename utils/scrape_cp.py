import asyncio
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
import re
import requests


def scrape(links=(None, None, None, None)):
    gfg, cf, cc, lc = links
    codingData = []

    chrome_options = Options()
    chrome_options.add_argument('--headless')  
    driver = webdriver.Chrome(options=chrome_options)
    if lc:
        try:
            username = lc.split("/")[-2]
            url = "https://leetcode.com/graphql"
            # Create a GraphQL client
            query = f"""
            {{
              userContestRanking(username: "{username}") {{
                rating
                topPercentage
              }}
              matchedUser(username: "{username}") {{
                submitStats: submitStatsGlobal {{
                  acSubmissionNum {{
                    difficulty
                    count
                  }}
                }}
              }}
            }}
            """
            headers = {
                "Content-Type": "application/json",
            }
            payload = {"query": query}
            response = requests.post(url, json=payload, headers=headers)
            data = response.json()["data"]
            lc_data = {
                "platform": "leetcode",
                "rating": data["userContestRanking"]["rating"],
                "topPercentage": data["userContestRanking"]["topPercentage"],
            }
            ac_submission_num = data["matchedUser"]["submitStats"]["acSubmissionNum"]
            for submission in ac_submission_num:
                difficulty = (
                    "problems_solved"
                    if submission["difficulty"] == "All"
                    else submission["difficulty"]
                )
                count = submission["count"]
                lc_data[difficulty] = count
            codingData.append(lc_data)
        except Exception as e:
            print("Couldn't fetch data: ", e)
    if gfg:        
        try:
            driver.get(gfg)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")

            # Extract data from the GFG page using BeautifulSoup
            problems_solved = (
                soup.find("div", class_="score_card")
                .find("span", class_="score_card_value")
                .text
            )
            level_wise = soup.find_all("li", class_="linksTypeProblem")
            level_data = {}
            for level in ["EASY", "MEDIUM", "HARD"]:
                for problem in level_wise:
                    if level in problem.text:
                        count = re.search(r"\d+", problem.text).group()
                        level_data[level] = count
                        break

            gfg_data = {
                "platform": "geeksforgeeks",
                "problems_solved": problems_solved,
                **level_data,
            }
            codingData.append(gfg_data)
        except Exception as e:
            print("Couldn't fetch data: ", e)

    if cf:        
        try:
            driver.get(cf)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")

            # Extract data from the CodeForces page using BeautifulSoup
            rating = soup.find("div", class_="info").find("li").text
            problems_solved = (
                soup.find("div", class_="_UserActivityFrame_countersRow")
                .find("div", class_="_UserActivityFrame_counterValue")
                .text
            )

            cf_data = {
                "platform": "codeforces",
                "rating": rating,
                "problems_solved": problems_solved,
            }
            codingData.append(cf_data)
        except Exception as e:
            print("Couldn't fetch data: ", e)        

    if cc:        
        try:
            driver.get(cc)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")

            # Extract data from the CodeChef page using BeautifulSoup
            max_rating = soup.find("div", class_="rating-header").find("small").text
            rating_cc = soup.find("div", class_="rating-number").text
            problems_cc = (
                soup.find("section", class_="problems-solved")
                .find("div", class_="content")
                .find("h5")
                .text
            )

            cc_data = {
                "platform": "codechef",
                "max_rating": max_rating,
                "rating": rating_cc,
                "problems_solved": problems_cc,
            }
            codingData.append(cc_data)
        except Exception as e:
            print("Couldn't fetch data: ", e)
    driver.quit()
    return codingData


class data_cleaning:
    def __init__(self) -> None:
        pass

    def extract_values(self, string):
        regex = r"(\d+)"
        matches = re.findall(regex, string)
        if len(matches) >= 2:
            value1 = matches[0]
            value2 = matches[1]
            return (value1, value2)
        elif len(matches) == 1:
            value1 = matches[0]
            return value1
        return None

    def remove_special_symbols(self, string):
        regex = r"[^\w\s]"
        return re.sub(regex, "", string)

    def clean_data(self, codingData):
        for data in codingData:
            if data["platform"] == "codeforces":
                data["rating"], data["max_rating"] = self.extract_values(data["rating"])
                data["problems_solved"] = self.extract_values(data["problems_solved"])
            elif data["platform"] == "codechef":
                data["max_rating"] = self.extract_values(data["max_rating"])
                data["problems_solved"] = self.extract_values(data["problems_solved"])
                # codingData[2]['stars'] = self.remove_special_symbols(codingData[2]['stars'])
        return codingData

    def grade_coding_profiles(self, codingData):
        total_problems = 0
        grade = {}
        grade["lc"] = grade["cc"] = grade["cf"] = grade["total_problems"] = 0
        for profiles in codingData:
            if profiles["platform"] == "lc":
                grade["lc"] = 5 - (int(profiles["topPercentage"]) / 20)
            # elif profiles['platform'] == 'gfg':
            elif profiles["platform"] == "cf":
                grade["cf"] = int(profiles["max_rating"]) / 4000 * 5
            elif profiles["platform"] == "cc":
                grade["cc"] = int(profiles["max_rating"]) / 3500 * 5
            total_problems += int(profiles["problems_solved"])
        if total_problems >= 1000:
            grade["total_problems"] = 5
        elif total_problems >= 800:
            grade["total_problems"] = 4
        elif total_problems >= 600:
            grade["total_problems"] = 3
        elif total_problems >= 400:
            grade["total_problems"] = 2
        elif total_problems >= 200:
            grade["total_problems"] = 1
        else:
            grade["total_problems"] = 0
        coding_grade = round(
            (grade["lc"] + grade["cc"] + grade["cf"] + grade["total_problems"]) / 4, 2
        )
        return coding_grade

def main():
    codingData = scrape()
    if len(codingData) > 0:
        cleaned_data = data_cleaning().clean_data(codingData)
        print(cleaned_data)

if __name__ == '__main__':
    import time
    start = time.time()
    main()
    print(time.time() - start)
