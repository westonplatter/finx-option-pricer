from dataclasses import dataclass, replace
from typing import List

import numpy as np
import pandas as pd

from finx_option_pricer.option import Option


@dataclass
class OptionsPlot:
    options: List[Option]
    spot_range: List
    strike_interval: float = 0.5

    def gen_value_df_timeincrementing(self, days: int, step: int = 1, show_final: bool = True):
        results = {"strikes": []}

        # NOTE - only look as far as the shortest dated option
        min_time = min([op.T for op in self.options])

        strike_range = np.arange(self.spot_range[0], self.spot_range[1], self.strike_interval)
        for price in strike_range:
            results["strikes"].append(price)

        for day in range(0, days + 1, step):
            combined_values = []
            for option in self.options:
                newT = min_time - (day / 365)
                newDays = int(newT * 365)

                if newT < 0.0:
                    continue

                results[newDays] = []

                values = []
                for price in strike_range:
                    x = Option(
                        S=price,
                        K=option.K,
                        T=newT,
                        r=option.r,
                        sigma=option.sigma,
                        option_type=option.option_type,
                    )
                    value = x.value - option.value
                    values.append(value)

                combined_values.append(values)

            combined_values = list(filter(None, combined_values))
            if combined_values == []:
                continue
            x = np.sum(combined_values, axis=0)
            if len(x) == 0.0:
                continue
            results[newDays] = x

        if show_final:
            values = []
            for price in strike_range:
                value = option.final_value(price)
                values.append(value)
            results[f"{option.id}-final"] = values

        # print(results)
        return pd.DataFrame(results)
        # return results

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
