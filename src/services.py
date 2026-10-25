"""Сервисы: кешбэк, инвесткопилка, поиск."""

from __future__ import annotations

import math
import re
from datetime import datetime
from typing import Any

import pandas as pd

from src import utils

# номера вида +7..., 8 (...), 8900...
PHONE_RE = re.compile(r"(?<!\d)(?:\+7|8)(?:[\s\-()]*\d){9,10}(?!\d)")
# ФИО вроде «Валерий А.»
PERSON_RE = re.compile(r"[А-ЯЁ][а-яё]+\s+[А-ЯЁ]\.")


def _matches_phone(text: str) -> bool:
    for m in PHONE_RE.finditer(text or ""):
        digits = re.sub(r"\D", "", m.group(0))
        if len(digits) in (10, 11) and digits[0] in "78":
            return True
    return False


def cashback_categories(
    data: pd.DataFrame | list[dict[str, Any]],
    year: int,
    month: int,
    rate: float = 0.01,
) -> dict[str, int]:
    """Кешбэк 1% по категориям за месяц (без Переводов и Наличных)."""
    if not 1 <= int(month) <= 12:
        raise ValueError("Месяц должен быть от 1 до 12")

    frame = utils.filter_successful(utils.ensure_frame(data))
    period = frame[
        (frame[utils.DATE_COLUMN].dt.year == int(year))
        & (frame[utils.DATE_COLUMN].dt.month == int(month))
    ]
    expenses = period[period[utils.PAYMENT_AMOUNT_COLUMN] < 0]
    expenses = expenses[
        ~expenses[utils.CATEGORY_COLUMN].isin(utils.TRANSFER_CATEGORIES)
    ]
    if expenses.empty:
        return {}

    result: dict[str, int] = {}
    grouped = expenses.groupby(utils.CATEGORY_COLUMN)[utils.PAYMENT_AMOUNT_COLUMN].sum()
    for category, amount in grouped.items():
        result[str(category)] = int(round(abs(float(amount)) * rate))

    return dict(sorted(result.items(), key=lambda x: x[1], reverse=True))


def investment_bank(
    month: str,
    transactions: list[dict[str, Any]] | pd.DataFrame,
    limit: int,
) -> float:
    """Сколько удалось бы отложить при округлении трат до limit (10/50/100)."""
    if int(limit) <= 0:
        raise ValueError("limit должен быть больше 0")

    frame = utils.ensure_frame(transactions)
    if utils.STATUS_COLUMN in frame.columns:
        frame = utils.filter_successful(frame)

    start = datetime.strptime(month, "%Y-%m")
    mask = (
        frame[utils.DATE_COLUMN].notna()
        & (frame[utils.DATE_COLUMN].dt.year == start.year)
        & (frame[utils.DATE_COLUMN].dt.month == start.month)
        & (frame[utils.AMOUNT_COLUMN] < 0)
    )
    target = frame[mask]
    if target.empty:
        return 0.0

    saved = 0.0
    for amount in target[utils.AMOUNT_COLUMN]:
        value = abs(float(amount))
        rounded = math.ceil(value / int(limit)) * int(limit)
        saved += rounded - value
    return round(saved, 2)


def simple_search(
    transactions: list[dict[str, Any]] | pd.DataFrame, query: str
) -> list[dict[str, Any]]:
    """Поиск по подстроке в описании или категории (без учёта регистра)."""
    text = (query or "").strip()
    if not text:
        return []

    frame = utils.ensure_frame(transactions)
    mask = frame[utils.DESCRIPTION_COLUMN].str.contains(
        text, case=False, regex=False, na=False
    ) | frame[utils.CATEGORY_COLUMN].str.contains(
        text, case=False, regex=False, na=False
    )
    return utils.to_records(frame[mask])


def phone_search(
    transactions: list[dict[str, Any]] | pd.DataFrame,
) -> list[dict[str, Any]]:
    """Транзакции, в описании которых есть мобильный номер."""
    frame = utils.ensure_frame(transactions)
    mask = frame[utils.DESCRIPTION_COLUMN].map(_matches_phone)
    return utils.to_records(frame[mask])


def transfers_to_people(
    transactions: list[dict[str, Any]] | pd.DataFrame,
) -> list[dict[str, Any]]:
    """Переводы физлицам: категория «Переводы» и описание вида «Имя Ф.»."""
    frame = utils.ensure_frame(transactions)
    mask = (
        frame[utils.CATEGORY_COLUMN].str.casefold() == "переводы"
    ) & frame[utils.DESCRIPTION_COLUMN].str.contains(PERSON_RE, regex=True, na=False)
    return utils.to_records(frame[mask])
