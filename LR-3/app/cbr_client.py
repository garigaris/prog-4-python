from xml.etree import ElementTree

import requests

from app.schemas import CurrencyRate

CBR_DAILY_URL = "https://www.cbr.ru/scripts/XML_daily.asp"


class CBRServiceError(Exception):
    pass


def _parse_float(value: str) -> float:
    return float(value.replace(",", "."))


def fetch_currency_rates() -> dict[str, CurrencyRate]:
    """Получает свежие курсы валют с XML API ЦБ РФ."""
    try:
        response = requests.get(CBR_DAILY_URL, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise CBRServiceError("Не удалось получить данные с сервера ЦБ РФ") from exc

    try:
        root = ElementTree.fromstring(response.content)
    except ElementTree.ParseError as exc:
        raise CBRServiceError("Сервер ЦБ РФ вернул некорректный XML") from exc

    date = root.attrib.get("Date", "")
    rates: dict[str, CurrencyRate] = {}

    for item in root.findall("Valute"):
        nominal = int(item.findtext("Nominal", "1"))
        value = _parse_float(item.findtext("Value", "0"))
        char_code = item.findtext("CharCode", "").upper()

        if not char_code:
            continue

        rates[char_code] = CurrencyRate(
            num_code=item.findtext("NumCode", ""),
            char_code=char_code,
            nominal=nominal,
            name=item.findtext("Name", ""),
            value=value,
            unit_value=value / nominal,
            date=date,
        )

    return rates


def fetch_currency_rate(char_code: str) -> CurrencyRate | None:
    rates = fetch_currency_rates()
    return rates.get(char_code.upper())
