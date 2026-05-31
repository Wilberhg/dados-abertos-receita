from datetime import datetime, timedelta


def coleta_data_atual():
    return datetime.today()
    # return datetime(2026, 8, 1)


def formata_data_base(data: datetime):
    data_base = data.strftime("%Y-%m")
    return data_base


def subtrai_data_base(data_base: str):
    data_base = datetime.strptime(data_base, "%Y-%m")
    data_base = data_base - timedelta(days=data_base.day)
    return formata_data_base(data_base)
