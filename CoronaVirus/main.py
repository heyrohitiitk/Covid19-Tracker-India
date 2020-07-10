from bs4 import BeautifulSoup
import requests
import pandas as pd
from prettytable import PrettyTable
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import json
import gmail
import logging
import argparse


def setLog(msg=None):
    FORMAT = "[%(asctime)-15s]: %(levelname)s :%(message)s"
    logging.basicConfig(
        level=logging.DEBUG, filename="test.log", format=FORMAT,
    )
    logging.error(msg)


class Tracker(object):
    def __init__(self):
        self.url = "https://www.mohfw.gov.in"
        self.page = requests.get(self.url)
        self.soup = BeautifulSoup(self.page.content, "html.parser")
        self.error = False
        # self.at_time = current time
        # self.data_set = dataframe
        # self.quick_list = dictionary of summary
        # self.stat = rows data
        # self.test_done
        # self.query_email

    def fetchData(self):
        try:
            soup = self.soup

            ## Enquiry Email
            email_head = soup.find("div", class_="header-bar")
            email_div = email_head.find("div", class_="row")
            self.test_done = email_div.find("span").text.replace("\n", "")
            self.query_email = email_div.find("a").text.replace("\n", "")

            # print(self.test_done)
            # print(self.query_email)

            ## Fetching The Overall Stats
            self.quick_list = {}
            result = soup.find("div", class_="site-stats-count")
            for lis in result.find_all("li"):
                try:
                    key = lis.span.text.replace("\n", "")
                    value = lis.strong.text.replace("\n", "")

                    self.quick_list[key.strip()] = int(value)
                except:
                    break
            # print(quick_list)

            # Fetch the Current Time
            time_div = soup.find("div", class_="status-update")
            time = time_div.find("span").text.replace("\n", "").strip()
            self.at_time = time[8:10] + "," + time[11:]
            # print(self.at_time)

            # Fetch The Table
            match = soup.find("div", class_="data-table")
            thead = match.find("thead")
            column = []
            for col in thead.find_all("th"):
                column.append(col.text.replace("\n", "").strip("*"))

            tbody = soup.find("tbody")
            stats = []
            all_rows = tbody.find_all("tr")
            extract_contents = lambda row: [x.text.replace("\n", "") for x in row]
            for row in all_rows:
                stat = extract_contents(row.find_all("td"))

                if len(stat) == len(column):
                    stats.append(stat)
            stats = stats[:-2] + stats[-1:]
            self.stat = stats
            col_names = [
                "S.No",
                "States",
                "Active Cases",
                "Recovered",
                "Deaths",
                "Confirmed",
            ]
            df = pd.DataFrame(data=stats, columns=col_names)
            df["Active Cases"] = df["Active Cases"].map(int)
            df["Recovered"] = df["Recovered"].map(int)
            df["Deaths"] = df["Deaths"].map(int)
            df["Confirmed"] = df["Confirmed"].map(int)
            new_state = []
            for x in df["States"]:
                new_state.append(x.lower())
            df["States"] = new_state
            self.data_set = df
            # print(self.data_set)
        except Exception as e:
            self.error = True
            msg = f"Script Failed Due to Error in Fetching Data:{e.__class__.__name__}"
            setLog(msg)
            gmail.sendError(self, msg)

    def showCoronaDataset(self):
        data = self.data_set
        table = PrettyTable()
        table.field_names = data.columns
        for i in self.stat[:-1]:
            table.add_row(i)
        self.corona_table = table
        print(table)
        print("Data as on :", self.at_time)
        print("Enquiry email : ", self.query_email)
        print(self.test_done)
        print("Overall Status :", self.quick_list)

    def barGraph(self):
        data = self.data_set.iloc[:-1]
        plt.figure(figsize=(15, 10))
        bar_h = [int(x) for x in data["Confirmed"]]
        bar_label = data["States"]
        bar_x = np.arange(len(bar_label))
        total_case = sum([int(x) for x in self.quick_list.values()])
        bar_plot = plt.bar(bar_x, bar_h, label=f"Total Cases :{total_case}")

        def autolabel(rects):
            for idx, rect in enumerate(bar_plot):
                height = rect.get_height()
                plt.text(
                    rect.get_x() + rect.get_width() / 2.0,
                    1.05 * height,
                    bar_h[idx],
                    ha="center",
                    va="bottom",
                    rotation=90,
                )

        autolabel(bar_plot)
        plt.legend()
        plt.xlabel("States/UT", fontsize=14)
        plt.ylabel("No. of Confirmed cases", fontsize=14)
        plt.title("Total Confirmed Cases Statewise", fontsize=18)
        plt.xticks(bar_x, bar_label, fontsize=6, rotation=90)
        plt.savefig("covid_bar_graph.png", bbox_inches="tight")
        plt.show()

    def donutChart(self):
        data = self.data_set.iloc[:-1]
        group_size = [
            sum([int(x) for x in self.quick_list.values()]),
            sum(data["Recovered"].map(int)),
            int(self.quick_list["Active Cases"]),
            sum(data["Deaths"].map(int)),
        ]
        group_labels = [
            "Confirmed\n" + str(sum([int(x) for x in self.quick_list.values()])),
            "Recovered\n" + str(sum(data["Recovered"].map(int))),
            "Active Cases\n" + str(self.quick_list["Active Cases"]),
            "Deaths\n" + str(sum(data["Deaths"].map(int))),
        ]

        custom_colors = ["skyblue", "yellowgreen", "blue", "red"]

        plt.figure(figsize=(5, 5))
        plt.pie(group_size, labels=group_labels, colors=custom_colors)
        central_circle = plt.Circle((0, 0), 0.5, color="white")
        fig = plt.gcf()
        fig.gca().add_artist(central_circle)
        plt.rc("font", size=12)
        plt.title(
            "Nationwide Total Confirmed, Recovered, Active and Death Cases", fontsize=20
        )
        plt.savefig("covid_donut_graph.png", bbox_inches="tight")
        # plt.show()

    def sendEMail(self, state):
        try:
            gmail.sendMail(self, state)
        except Exception as e:
            msg = f"Exception Occured in main.py->sendMail(): {e.__class__.__name__} : {e}"
            setLog(msg)
            gmail.sendError(self, msg)


if __name__ == "__main__":
    covid = Tracker()
    covid.fetchData()
    covid.donutChart()
    # state = "madhya pradesh"
    # if not covid.error:
    #     covid.sendEMail(state)

    choose_state = [x.lower() for x in covid.data_set["States"]]
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", help="states")
    args = parser.parse_args()

    if args.state in choose_state:
        if not covid.error:
            covid.sendEMail(args.state)
        covid.showCoronaDataset()
    else:
        print(f"No such state : {args.state}")
    # covid.barGraph()
    # print(sum(covid.data_set.iloc[:-1]["Confirmed"]))

