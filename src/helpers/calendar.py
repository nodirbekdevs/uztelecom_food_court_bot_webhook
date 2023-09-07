from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta


def set_before_zero(num):
    return ("0" + str(num))[-2:]


def get_num_day_of_week(date):
    day = date.weekday()
    # return 6 if day == 0 else day - 1
    return day


def get_days(year, month):
    d = datetime(year, month, 1)
    days = [[]]

    for _ in range(get_num_day_of_week(d)):
        days[-1].append("-")

    while d.month == month:
        days[-1].append(d.day)
        if get_num_day_of_week(d) % 7 == 6:
            days.append([])
        d += timedelta(days=1)

    if get_num_day_of_week(d) != 0:
        for _ in range(get_num_day_of_week(d), 7):
            days[-1].append("-")

    for sublist in days:
        if sublist[-1] != '-':
            sublist[-1] = "-"
        if sublist[-2] != "-":
            sublist[-2] = "-"

    return days


def is_last_day_of_month():
    current_date = datetime.today()

    next_day = current_date + timedelta(days=1)

    if next_day.month != current_date.month:
        return dict(year=next_day.year, month=next_day.month, current_date=next_day.day, date=current_date.day)

    return dict(year=current_date.year, month=current_date.month, current_date=current_date.day)


def calendar(year, month, current_date, date=None):
    current_month_date = datetime(year, month, 1)
    day_lines = get_days(year, month)

    current_info = f"{set_before_zero(current_month_date.month)}-{current_month_date.year}"

    buttons = [[
        InlineKeyboardButton(text=current_info, callback_data=f"info_{current_info}")
    ]]

    for line in day_lines:
        buttons.append([])
        for day in line:
            cd = "-"
            if day != '-':
                if date and day != current_date:
                    cd = day
                elif date and day == current_date:
                    cd = day
                elif not date and day != current_date and day > current_date:
                    cd = day
                else:
                    cd = "-"
            # cd = day if day != '-' and day != current_date else '-'
            callback_data_value = f"day_{set_before_zero(cd)}-{current_info}" if cd != '-' else "none"

            buttons[-1].append(
                InlineKeyboardButton(
                    text=str(cd),
                    callback_data=callback_data_value
                )
            )

    return InlineKeyboardMarkup(inline_keyboard=buttons)
