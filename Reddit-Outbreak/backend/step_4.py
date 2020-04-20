from step_3 import Pandemic
from setup import SetUp

from pathlib import Path
from utils import log

from bokeh.plotting import figure, show
from bokeh.palettes import Set1_3
from bokeh.models import HoverTool
from bokeh.io import export_png

import pandas as pd
from datetime import timedelta
from heapq import nlargest
import subprocess

import json

PALETT = list(Set1_3)
PALETT = PALETT[0], "black", PALETT[2]


class Analyser(object):
    """Analyses the outbreak and creates the json for
    visualisation."""

    def __init__(self, context, intervals: str="1min"):
        super(Analyser, self).__init__()

        # setup path to databases
        self.db_folder = Path(context.db_folder)

        self.subreddit_db_path = self.db_folder / "subreddit.json"

        # setup reddit api interface
        self.reddit = context.reddit_api

        # get link to pandemics
        self.pandemic_instance = Pandemic(context)

        self.delta = pd.to_timedelta(intervals)

        self.plots_folder = self.db_folder / "plots"
        self.plots_folder.mkdir(parents=True, exist_ok=True)

    def iter_outbreaks(self):
        for outbreak in self.pandemic_instance.iter_over_outbreaks():

            outbreak_path = outbreak["pandemic_dir"]
            csv_name = f"{outbreak['name']}.csv"
            outbreak_csv = outbreak_path / csv_name

            outbreak["csv_file"] = outbreak_csv

            yield outbreak

    def iter_csv(self):
        for outbreak in self.iter_outbreaks():
            df = pd.read_csv(outbreak["csv_file"])
            df["T"] = pd.to_datetime(df["T"], unit="s")

            df.index = df["T"]
            del df["T"]

            df = df.astype("int32")

            df = df.resample(self.delta).bfill()

            # if we have more than 100 observations, resample
            # with 1 minute bigger bins
            if len(df) > 60:
                self.delta += timedelta(minutes=1)
                df = df.resample(self.delta).bfill()

            yield df, outbreak

    def max_infected(self, top: int=10) -> iter:

        # key function finding number of infected
        def key(csv):
            df, outbreak = csv
            return float(df["In"].tail(1))

        return nlargest(top, self.iter_csv(), key)

    def create_plot(self, df, context):
        p = figure(x_axis_type="datetime",
                   title=f"Rovid-19 Outbreak in \\r\\{context['name']}")

        p.title.text_color = "white"

        translate = dict(In="Infected",
                         D="Dead",
                         R="Recovered")

        vbars = p.vbar_stack(["In", "D", "R"],
                             x="T",
                             color=PALETT,
                             width=self.delta,
                             source=df,
                             legend_label=list(translate.values()),
                             alpha=0.96)

        p.legend.location = "top_left"

        p.background_fill_color = '#2F2F2F'
        p.border_fill_color = '#2F2F2F'
        p.outline_line_color = '#444444'

        p.xaxis.axis_line_color = "white"
        p.xaxis.axis_label_text_color = "white"
        p.xaxis.major_label_text_color = "white"
        p.xaxis.major_tick_line_color = "white"
        p.xaxis.minor_tick_line_color = "white"
        p.xaxis.minor_tick_line_color = "white"

        p.yaxis.axis_line_color = "white"
        p.yaxis.axis_label_text_color = "white"
        p.yaxis.major_label_text_color = "white"
        p.yaxis.major_tick_line_color = "white"
        p.yaxis.minor_tick_line_color = "white"
        p.yaxis.minor_tick_line_color = "white"
        p.y_range.start = 0

        # adding hover tool
        for bar in vbars:

            kind = bar.name
            hover = HoverTool(tooltips=[
                (f"{translate[kind]}", f"@{kind}%")
            ], renderers=[bar])
            p.add_tools(hover)

        save_path = self.plots_folder / f"{context['name']}.png"
        return p, save_path

    def create_pngs(self):

        for df, context in self.max_infected():
            p, path = self.create_plot(df, context)
            export_png(p, filename=path)

    def create_db(self):

        db = {}
        for df, context in self.max_infected():

            # convert to unix time
            df["Time"] = df.index.view("int64") // 10**6

            # convert df to dict
            csv_to_json = df.to_dict(orient="records")
            reduced_context = df.tail(1).to_dict(orient="records")[0]

            # create dict for c3.js
            json_object = {context["name"]: {
                "data": csv_to_json, "state": reduced_context}}
            db.update(json_object)

        # save it to disk
        with open("/home/levi/Stats/data-playground/db.json", "w") as db_file:
            json.dump(db, db_file)

    def push(self):
        subprocess.call("bash push.sh", shell=True)


if __name__ == '__main__':
    setup = SetUp()
    setup.load_db()

    context = setup.context

    viz = Analyser(context)

    for _ in viz.iter_csv():
        pass
