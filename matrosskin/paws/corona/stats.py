import os
from datetime import timedelta, datetime

import pandas as pd
from  matplotlib import use as use_mpl
import matplotlib.pyplot as plt
from pandas.plotting import table

import config

pd.set_option("display.max_columns", None)
use_mpl("Agg")


STATS_URL = (
    "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/"
    "csse_covid_19_time_series/"
)
STORE_PATH = os.path.join(config.data_path, "corona_stats")
ALWAYS_PRESENT_COUNTRIES = ["Finland", "Australia", "Estonia"]


def get_fresh_data():
    confirmed = pd.read_csv(
        f"{STATS_URL}time_series_covid19_confirmed_global.csv", sep=","
    )
    deaths = pd.read_csv(f"{STATS_URL}time_series_covid19_deaths_global.csv", sep=",")
    recovered = pd.read_csv(
        f"{STATS_URL}time_series_covid19_recovered_global.csv", sep=","
    )

    # Convert data to format 'dd.mm.yy'
    new_cols = list(confirmed.columns[:4]) + list(
        confirmed.columns[4:].map(
            lambda x: "{0:02d}.{1:02d}.{2:d}".format(
                int(x.split(sep="/")[1]),
                int(x.split(sep="/")[0]),
                int(x.split(sep="/")[2]),
            )
        )
    )
    confirmed.columns = new_cols
    recovered.columns = new_cols
    deaths.columns = new_cols

    return confirmed, deaths, recovered


def get_file_path(type: str, date: str) -> str:
    file_path = os.path.join(STORE_PATH, f"{type}_{date}.png")
    return file_path


def get_daily_stats(confirmed, deaths, recovered):
    """Create tables with daily adds."""

    confirmed_daily = confirmed.copy()
    confirmed_daily.iloc[:, 4:] = confirmed_daily.iloc[:, 4:].diff(axis=1)
    deaths_daily = deaths.copy()
    deaths_daily.iloc[:, 4:] = deaths_daily.iloc[:, 4:].diff(axis=1)
    recovered_daily = recovered.copy()
    recovered_daily.iloc[:, 4:] = recovered_daily.iloc[:, 4:].diff(axis=1)

    return confirmed_daily, deaths_daily, recovered_daily


def get_smooth_daily(confirmed_daily):
    """Create table with smothed add of sickenings."""

    smooth_conf_daily = confirmed_daily.copy()
    smooth_conf_daily.iloc[:, 4:] = (
        smooth_conf_daily.iloc[:, 4:]
            .rolling(window=8, min_periods=2, center=True, axis=1)
            .mean()
    )
    smooth_conf_daily.iloc[:, 4:] = smooth_conf_daily.iloc[:, 4:].round(1)

    return smooth_conf_daily


def get_confirmed_top(last_date, confirmed, deaths, smooth_conf_daily):

    # Get top 20 countries with confirmed cases
    confirmed_top = (
        confirmed.iloc[:, [1, -1]]
            .groupby("Country/Region")
            .sum()
            .sort_values(last_date, ascending=False)
            .head(20)
    )

    countries = list(confirmed_top.index)
    # Add other countries
    countries += ALWAYS_PRESENT_COUNTRIES
    # Create summaru table by countries
    confirmed_top = confirmed_top.rename(columns={str(last_date): "total_confirmed"})
    dates = [i for i in confirmed.columns[4:]]

    for country in countries:

        confirmed_top.loc[country, "total_confirmed"] = confirmed.loc[
                                                        confirmed["Country/Region"] == country, :
                                                        ].sum()[4:][-1]
        confirmed_top.loc[country, "last_day_conf"] = (
                confirmed.loc[confirmed["Country/Region"] == country, :].sum()[-1]
                - confirmed.loc[confirmed["Country/Region"] == country, :].sum()[-2]
        )
        confirmed_top.loc[country, "mortality, %"] = round(
            deaths.loc[deaths["Country/Region"] == country, :].sum()[4:][-1]
            / confirmed.loc[confirmed["Country/Region"] == country, :].sum()[4:][-1]
            * 100,
            1,
        )

        # Consider max of trend as peak of epidemy
        smoothed_conf_max = round(
            smooth_conf_daily[smooth_conf_daily["Country/Region"] == country]
                .iloc[:, 4:]
                .sum()
                .max(),
            2,
        )
        peak_date = (
            smooth_conf_daily[smooth_conf_daily["Country/Region"] == country]
                .iloc[:, 4:]
                .sum()
                .idxmax()
        )
        peak_day = dates.index(peak_date)

        # Get data of begining of epidemy as data then number of confirmed > 1% from max of daily cases
        start_day = (
                smooth_conf_daily[smooth_conf_daily["Country/Region"] == country]
                .iloc[:, 4:]
                .sum()
                < smoothed_conf_max / 100
        ).sum()
        start_date = dates[start_day - 1]

        confirmed_top.loc[country, "trend_max"] = smoothed_conf_max
        confirmed_top.loc[country, "start_date"] = start_date
        confirmed_top.loc[country, "peak_date"] = peak_date
        confirmed_top.loc[country, "peak_passed"] = (
                round(
                    smooth_conf_daily.loc[
                        smooth_conf_daily["Country/Region"] == country, last_date
                    ].sum(),
                    2,
                )
                != smoothed_conf_max
        )
        confirmed_top.loc[country, "days_to_peak"] = peak_day - start_day

        # If peak value passed calculate value of finalizing of epidemy
        if confirmed_top.loc[country, "peak_passed"]:
            confirmed_top.loc[country, "end_date"] = (
                    datetime.strptime(
                        confirmed_top.loc[country, "peak_date"] + "20", "%d.%m.%Y"
                    ).date()
                    + timedelta(confirmed_top.loc[country, "days_to_peak"])
            ).strftime("%d.%m.%Y")

    # Fix for China
    confirmed_top.loc["China", "start_date"] = "22.01.20"

    return confirmed_top


def common_stats() -> str:
    confirmed, deaths, recovered = get_fresh_data()

    last_date = confirmed.columns[-1]

    file_path = get_file_path("common", last_date)
    if os.path.exists(file_path):
        return file_path

    confirmed_top = (
        confirmed.iloc[:, [1, -1]]
        .groupby("Country/Region")
        .sum()
        .sort_values(last_date, ascending=False)
        .head(20)
    )
    # Calculate ratio of sickening by countries
    conf_top_ratio = confirmed_top.sum() / confirmed.iloc[:, 4:].sum()[-1]

    # Create legends
    l1 = "Infected at " + last_date + " - " + str(confirmed.iloc[:, 4:].sum()[-1])
    l2 = "Recovered at " + last_date + " - " + str(recovered.iloc[:, 4:].sum()[-1])
    l3 = "Dead at " + last_date + " - " + str(deaths.iloc[:, 4:].sum()[-1])

    # Output graphics
    fig, ax = plt.subplots(figsize=[16, 6])
    ax.plot(confirmed.iloc[:, 4:].sum(), "-", alpha=0.6, color="orange", label=l1)
    ax.plot(recovered.iloc[:, 4:].sum(), "-", alpha=0.6, color="green", label=l2)
    ax.plot(deaths.iloc[:, 4:].sum(), "-", alpha=0.6, color="red", label=l3)

    ax.legend(loc="upper left", prop=dict(size=12))
    ax.xaxis.grid(which="minor")
    ax.yaxis.grid()
    ax.tick_params(axis="x", labelrotation=90)
    plt.title(
        "COVID-19 in all countries. Top 20 countries consists {:.2%} of total confirmed infected cases.".format(
            conf_top_ratio[0]
        )
    )
    plt.savefig(file_path, bbox_inches="tight", dpi=75)

    return file_path


def top_countries() -> str:
    confirmed, deaths, recovered = get_fresh_data()
    last_date = confirmed.columns[-1]
    file_path = get_file_path("top", last_date)
    if os.path.exists(file_path):
        return file_path

    confirmed_daily, _, _ = get_daily_stats(confirmed, deaths, recovered)
    smooth_conf_daily = get_smooth_daily(confirmed_daily)
    confirmed_top = get_confirmed_top(last_date, confirmed, deaths, smooth_conf_daily)

    # save to the file
    fig, ax = plt.subplots(figsize=(26, 13))  # set size frame
    ax.xaxis.set_visible(False)  # hide the x axis
    ax.yaxis.set_visible(False)  # hide the y axis
    ax.set_frame_on(False)  # no visible frame, uncomment if size is ok
    tabla = table(
        ax,
        confirmed_top,
        loc="upper left",
        colWidths=[0.05] * len(confirmed_top.columns),
    )  # where df is your data frame
    tabla.auto_set_font_size(False)  # Activate set fontsize manually
    tabla.set_fontsize(20)  # if ++fontsize is necessary ++colWidths
    tabla.scale(2.4, 2.4)  # change size table
    plt.savefig(file_path, transparent=True)

    return file_path


def by_country(country: str) -> str:

    if country.lower() == "us":
        country = country.upper()
    else:
        country = country.title()

    confirmed, deaths, recovered = get_fresh_data()
    last_date = confirmed.columns[-1]
    file_path = get_file_path(f"by_country_{country}", last_date)
    if os.path.exists(file_path):
        return file_path

    confirmed_daily, deaths_daily, recovered_daily = get_daily_stats(confirmed, deaths, recovered)
    smooth_conf_daily = get_smooth_daily(confirmed_daily)
    confirmed_top = get_confirmed_top(last_date, confirmed, deaths, smooth_conf_daily)

    if country not in list(confirmed_top.index):
        return ''

    # Legend
    l1 = 'Infected at ' + last_date + ' - ' + str(confirmed.loc[confirmed['Country/Region'] == country, :].sum()[-1])
    l2 = 'Recovered at ' + last_date + ' - ' + str(recovered.loc[recovered['Country/Region'] == country, :].sum()[-1])
    l3 = 'Dead at ' + last_date + ' - ' + str(deaths.loc[deaths['Country/Region'] == country, :].sum()[-1])

    # Tmp dataframe with data for country
    df = pd.DataFrame(confirmed_daily.loc[confirmed_daily['Country/Region'] == country, :].sum()[4:])
    df.columns = ['confirmed_daily']
    df['recovered_daily'] = recovered_daily.loc[recovered_daily['Country/Region'] == country, :].sum()[4:]
    df['deaths_daily'] = deaths_daily.loc[deaths_daily['Country/Region'] == country, :].sum()[4:]
    df['deaths_daily'] = deaths_daily.loc[deaths_daily['Country/Region'] == country, :].sum()[4:]
    df['smooth_conf_daily'] = smooth_conf_daily.loc[smooth_conf_daily['Country/Region'] == country, :].sum()[4:]

    # Graphic
    fig, ax = plt.subplots(figsize=[16, 6], nrows=1)
    plt.title('COVID-19 dinamics daily in ' + country)

    ax.bar(df.index, df.confirmed_daily, alpha=0.5, color='orange', label=l1)
    ax.bar(df.index, df.recovered_daily, alpha=0.6, color='green', label=l2)
    ax.bar(df.index, df.deaths_daily, alpha=0.7, color='red', label=l3)
    ax.plot(df.index, df.smooth_conf_daily, alpha=0.7, color='black')

    # Add dates of beginning end ending of peak
    start_date = confirmed_top[confirmed_top.index == country].start_date.iloc[0]
    start_point = smooth_conf_daily.loc[smooth_conf_daily['Country/Region'] == country, start_date].sum()
    ax.plot_date(start_date, start_point, 'o', alpha=0.7, color='black')
    shift = confirmed_top.loc[confirmed_top.index == country, 'trend_max'].iloc[0] / 40
    plt.text(start_date, start_point + shift, 'Start at ' + start_date, ha='right', fontsize=20)

    peak_date = confirmed_top[confirmed_top.index == country].peak_date.iloc[0]
    peak_point = smooth_conf_daily.loc[smooth_conf_daily['Country/Region'] == country, peak_date].sum()
    ax.plot_date(peak_date, peak_point, 'o', alpha=0.7, color='black')
    plt.text(peak_date, peak_point + shift, 'Peak at ' + peak_date, ha='right', fontsize=20)

    ax.xaxis.grid(False)
    ax.yaxis.grid(False)
    ax.tick_params(axis='x', labelrotation=90)
    ax.legend(loc='upper left', prop=dict(size=12))

    # Output country name
    max_pos = max(df['confirmed_daily'].max(), df['recovered_daily'].max())
    if confirmed_top[confirmed_top.index == country].peak_passed.iloc[0]:
        estimation = 'peak is passed - end of infection ' + confirmed_top[confirmed_top.index == country].end_date.iloc[
            0]
    else:
        estimation = 'peak is not passed - end of infection is not clear'
    plt.text(df.index[len(df.index) // 2], 3 * max_pos // 4, country, ha='center', fontsize=50)
    plt.text(df.index[len(df.index) // 2], 2 * max_pos // 3, estimation, ha='center', fontsize=20)

    plt.savefig(file_path, transparent=True)

    return file_path
