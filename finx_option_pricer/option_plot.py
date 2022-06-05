from dataclasses import dataclass
from typing import List

import numpy as np
import pandas as pd

from finx_option_pricer.option import Option

MARKET_DAYS_PER_YEAR = 252


@dataclass
class OptionPosition:
    option: Option
    quantity: int
    end_sigma: float = None

    SHORT = "short"
    LONG = "long"

    @property
    def id(self):
        side = self.LONG if self.quantity >= 1 else self.SHORT
        qty = abs(self.quantity)
        return f"{self.option.id}-{side}{qty}"

    def interpolated_vol(self, fraction: float) -> float:
        """Using the start and end IV, calc the linear interpolated IV"""
        assert self.end_sigma is not None, "end_sigma must be not None"
        return self.option.sigma - (self.option.sigma - self.end_sigma) * fraction


@dataclass
class OptionsPlot:
    option_positions: List[OptionPosition]
    spot_range: List
    strike_interval: float = 0.5

    @property
    def initial_value(self) -> float:
        """Returns the aggregate value for the option_options

        Returns:
            float: aggregate value for self.option_options
        """
        total_value = 0.0
        for op in self.option_positions:
            total_value += op.option.value * op.quantity
        return total_value

    # flake8: noqa: C901
    # TODO - resolve C901 issue
    def gen_value_df_timeincrementing(
        self, days: int, step: int = 1, show_final: bool = True, market_days_year: int = 252, value_relative=True
    ) -> pd.DataFrame:
        """Generate value option positions as they decay with time.

        Example return,

           strikes        10         5       0
        0     85.0 -1.358147 -1.858064 -1.9741
        1     85.5 -1.255539 -1.823718 -1.9741
        2     86.0 -1.139727 -1.781053 -1.9741
        3     86.5 -1.009635 -1.728572 -1.9741

        Args:
            days (int): number days to increment over.
            step (int, optional): step or increment interval. Defaults to 1.
            show_final (bool, optional): option(s) value at expiration of nearest data option. Defaults to True.
            market_days_year(int): number of market days in a calendar year. Defaults to 252.
            value_relative(boolean): value the options package with respect to initial value vs absolute value. Defaults to True.

        Returns:
            (pd.DataFrame): DataFrame with columns [strikes, days-step1, days-step2, ..., expiration]
        """
        results = {"strikes": []}

        # let's only call this once and store in private var
        __initial_value = self.initial_value

        # NOTE - only look as far as the shortest dated option
        min_time = min([op.option.T for op in self.option_positions])
        min_days = int(min_time * MARKET_DAYS_PER_YEAR)

        _start = self.spot_range[0]
        _end = self.spot_range[1] + self.strike_interval
        strike_range = np.arange(_start, _end, self.strike_interval)

        for price in strike_range:
            results["strikes"].append(price)

        # determine aggregate value as time passes
        for day in range(0, days + 1, step):
            if day >= min_days:
                continue

            annualized_days = day / MARKET_DAYS_PER_YEAR

            #
            # TODO - This could use a good refactoring. Too much going on at once
            #
            aggregate_position_value_wrt_strikes = []
            for option_position in self.option_positions:
                newT = option_position.option.T - annualized_days

                newDays = int(newT * MARKET_DAYS_PER_YEAR)

                # if the "option_position" has an end_sigma non None value, this means the option's sigma/vol
                # is expected to linearly change as the option progresses to expiration. For example,
                # consider SPY options that at 45dte (IV ~ 16-22 vol) compared to 7dte (IV ~ 10-14 vol)
                # The adjustments in vol are calculated within OptionPosition.interpolated_vol()
                sigma = option_position.option.sigma
                if option_position.end_sigma is not None:
                    fraction_to_dte = (option_position.option.T - newT) / option_position.option.T
                    sigma = option_position.interpolated_vol(fraction_to_dte)

                option_position_strike_values = []
                for price in strike_range:
                    x = Option(
                        S=price,
                        K=option_position.option.K,
                        T=newT,
                        r=option_position.option.r,
                        sigma=sigma,
                        option_type=option_position.option.option_type,
                    )
                    value = x.value * option_position.quantity
                    option_position_strike_values.append(value)

                aggregate_position_value_wrt_strikes.append(option_position_strike_values)

            results[newDays] = np.sum(aggregate_position_value_wrt_strikes, axis=0) - __initial_value

        # determine final value at expiration of nearest dated option
        #
        # TODO - This could use a good refactoring. Too much going on at once
        #
        if show_final:
            option_positions_values = []

            for option_position in self.option_positions:
                newT = option_position.option.T - min_time

                option_position_strike_values = []
                for price in strike_range:
                    value = None
                    if newT <= 1 / MARKET_DAYS_PER_YEAR:
                        # option has expired - determine final value
                        value = option_position.option.final_value(price) * option_position.quantity

                    else:
                        # option has not expired - determine pre-expiration value
                        x = Option(
                            S=price,
                            K=option_position.option.K,
                            T=newT,
                            r=option_position.option.r,
                            sigma=option_position.option.sigma,
                            option_type=option_position.option.option_type,
                        )
                        value = x.value * option_position.quantity
                    # append the value
                    option_position_strike_values.append(value)

                option_positions_values.append(option_position_strike_values)

            agg_value_sum = list(np.sum(option_positions_values, axis=0))
            results[0] = agg_value_sum - __initial_value if value_relative is True else agg_value_sum

        # return values as DataFrame
        return pd.DataFrame(results)
