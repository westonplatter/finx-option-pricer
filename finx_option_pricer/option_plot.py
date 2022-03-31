from dataclasses import dataclass, replace
import math
from re import L
from typing import List

from click import option

import numpy as np
import pandas as pd

from finx_option_pricer.option import Option


@dataclass
class OptionPosition:
    option: Option
    quantity: int

    @property
    def id(self):
        side = "long" if self.quantity >= 1 else "short"
        qty = abs(self.quantity)
        return f"{self.option.id}-{side}{qty}"


@dataclass
class OptionsPlot:
    option_positions: List[OptionPosition]
    spot_range: List
    strike_interval: float = 0.5

    def describe_option_positions(self):
        for op in self.option_positions:
            # print(op.id)
            pass
    
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



    def gen_value_df_timeincrementing(self, days: int, step: int = 1, show_final: bool = True) -> pd.DataFrame:
        """Generate value option positions as they decay with time.

        Example return,

           strikes        10         5       0
        0     85.0 -1.358147 -1.858064 -1.9741
        1     85.5 -1.255539 -1.823718 -1.9741
        2     86.0 -1.139727 -1.781053 -1.9741
        3     86.5 -1.009635 -1.728572 -1.9741

        Args:
            days (int): _description_
            step (int, optional): _description_. Defaults to 1.
            show_final (bool, optional): _description_. Defaults to True.

        Returns:
            (pd.DataFrame): _description_
        """
        results = {"strikes": []}

        # let's only call this once and store in private var
        __initial_value = self.initial_value

        # NOTE - only look as far as the shortest dated option
        min_time = min([op.option.T for op in self.option_positions])
        min_days = int(min_time * 252)

        _start = self.spot_range[0]
        _end = self.spot_range[1] + self.strike_interval
        strike_range = np.arange(_start, _end, self.strike_interval)

        for price in strike_range:
            results["strikes"].append(price)

        # determine aggregate value as time passes
        for day in range(0, days + 1, step):
            if day >= min_days:
                continue

            annualized_days = day / 252

            aggregate_position_value_wrt_strikes = []
            for option_position in self.option_positions:
                newT = option_position.option.T - annualized_days

                newDays = int(newT * 252)

                option_position_strike_values = []
                for price in strike_range:
                    x = Option(
                        S=price,
                        K=option_position.option.K,
                        T=newT,
                        r=option_position.option.r,
                        sigma=option_position.option.sigma,
                        option_type=option_position.option.option_type,
                    )
                    value = x.value * option_position.quantity
                    option_position_strike_values.append(value)

                aggregate_position_value_wrt_strikes.append(option_position_strike_values)

            results[newDays] = np.sum(aggregate_position_value_wrt_strikes, axis=0) - __initial_value

        # determine final value at expiration of nearest dated option
        if show_final:
            option_positions_values = []

            for option_position in self.option_positions:
                newT = option_position.option.T - min_time

                option_position_strike_values = []
                for price in strike_range:
                    value = None
                    if newT <= 1 / 252:
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
            results[0] = list(np.sum(option_positions_values, axis=0)) - __initial_value

        # return values as DataFrame
        return pd.DataFrame(results)

    def gen_value_df(self):
        results = {"strikes": []}

        strike_range = np.arange(self.spot_range[0], self.spot_range[1], self.strike_interval)

        for price in strike_range:
            results["strikes"].append(price)

        for option in self.options:
            option_id = option.id
            x = replace(option)
            values = []

            for price in strike_range:
                x.S = price
                value = x.value
                values.append(value)
            results[option_id] = values
            del values

        return pd.DataFrame(results)
