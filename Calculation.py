import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay

holidays = USFederalHolidayCalendar()
usb = CustomBusinessDay(calendar=holidays)

all_days = pd.date_range("2026-01-01", "2027-12-31", freq='D')
biz_days = pd.date_range("2026-01-01", "2027-12-31", freq=usb)
biz_days_set = set(biz_days)

fomc_dates = [
    "2026-01-28","2026-03-18","2026-04-29","2026-06-17",
    "2026-07-29","2026-09-16","2026-10-28","2026-12-09",
    "2027-01-27","2027-03-17","2027-04-28","2027-06-16",
    "2027-07-28","2027-09-22","2027-11-03","2027-12-15"
]

month_options = pd.date_range(
    "2026-01-01",
    periods=24,
    freq='MS'
).strftime('%b-%y').tolist()


def get_daily_series(base_val, sliders_dict, mp, qp, yp):

    daily = pd.Series(base_val, index=all_days)
    running = base_val

    for d_str in sorted(fomc_dates):
        m_date = pd.Timestamp(d_str)
        next_biz = m_date + usb
        running += sliders_dict[d_str] / 100
        daily.loc[next_biz:] = running

    for (year, month), group in daily.groupby([daily.index.year, daily.index.month]):
        month_biz = [d for d in group.index if d in biz_days_set]
        if month_biz:
            lwd = max(month_biz)
            if lwd.month == 12:
                p_val = yp
            elif lwd.month in [3, 6, 9]:
                p_val = qp
            else:
                p_val = mp
            daily.loc[lwd] += p_val / 100

    return daily


def compute_monthly(effr_spot, sofr_spot, sliders_dict, mp, qp, yp):

    effr_daily = get_daily_series(effr_spot, sliders_dict, mp, qp, yp)
    sofr_daily = get_daily_series(sofr_spot, sliders_dict, mp, qp, yp)

    df = pd.DataFrame(index=month_options)

    df['EFFR_Avg'] = effr_daily.groupby(
        [effr_daily.index.year, effr_daily.index.month]
    ).mean().values

    df['SOFR_Avg'] = sofr_daily.groupby(
        [sofr_daily.index.year, sofr_daily.index.month]
    ).mean().values

    df['ZQ_Outright'] = 100 - df['EFFR_Avg']
    df['SR1_Outright'] = 100 - df['SOFR_Avg']

    return effr_daily, sofr_daily, df
