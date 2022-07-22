import pandas as pd


def calc_max_profit(df):
    """
    Calculate the max profit of a given option structure.
    """
    max_profit = df[df.columns[-1]].max()
    return max_profit


def calc_max_loss(df):
    """
    Calculate the max loss of a given option structure.
    """
    max_loss = df[df.columns[-1]].min()
    return max_loss


def calc_max_loss_strike(df, lower_strike, upper_strike):
    """
    Calculate the max loss of a given option structure.
    """
    series = df[df.columns[-1]]
    max_loss = series[(series.index >= lower_strike) & (series.index <= upper_strike)].min()
    return max_loss