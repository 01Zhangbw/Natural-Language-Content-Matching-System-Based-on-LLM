# 判断是否为日期
def is_date(string, fuzzy=False):
    # Parse a string into a date and check its validity
    try:
        dateutil.parser.parse(string, fuzzy=fuzzy)
        return True
    except ValueError:
        return False

# 格式化日期
def format_date(d):
    # Standardize the date format for each search result
    date = dateutil.parser.parse(current_date, fuzzy=True).strftime("%b %d, %Y")
    if d is None:
        return None

    for t in ["second", "minute", "hour"]:
        if f"{t} ago" in d or f"{t}s ago" in d:
            return date

    t = "day"
    if f"{t} ago" in d or f"{t}s ago" in d:
        n_days = int(re.search("(\d+) days? ago", d).group(1))
        return (
            datetime.datetime.strptime(date, "%b %d, %Y")
            - datetime.timedelta(days=n_days)
        ).strftime("%b %d, %Y")

    try:
        return dateutil.parser.parse(d, fuzzy=True).strftime("%b %d, %Y")
    except ValueError:
        for x in d.split():
            if is_date(x):
                return dateutil.parser.parse(x, fuzzy=True).strftime("%b %d, %Y")
