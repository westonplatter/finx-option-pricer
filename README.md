# Finx IB Reports
Python package to fetch reports from IB.

## Example

Example `.env` file,
```
IB_FLEX_TOKEN=1111111222222233333

IB_REPORT_ID_MYREPORT=123456
```

Example python,
```
from finx_ib_reports.download_trades import execute
report_name = "myreport"
execute(report_name)
```

And checkout the reports in `data`.


## License
BSD-3. See LICENSE file.
