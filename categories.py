from typing import Dict, List, NamedTuple

import db


class Category(NamedTuple):
    """Структура категории"""
    codename: str
    name: str
    aliases: List[str]


class Categories:
    def __init__(self):
        self._categories = self._load_categories()

    def _load_categories(self) -> List[Category]:
        """Возвращает справочник категорий расходов из БД"""
        categories = db.fetchall(
            "category", "codename name aliases".split()
        )
        categories = self._fill_aliases(categories)
        return categories

    def _fill_aliases(self, categories: List[Dict]) -> List[Category]:
        """Заполняет по каждой категории aliases, то есть возможные
        названия этой категории, которые можем писать в тексте сообщения.
        Например, категория «кафе» может быть написана как cafe,
        ресторан и тд."""
        categories_result = []
        for index, category in enumerate(categories):
            aliases = category["aliases"].split(",")
            aliases = list(filter(None, map(str.strip, aliases)))
            aliases.append(category["codename"])
            aliases.append(category["name"])
            categories_result.append(Category(
                codename=category['codename'],
                name=category['name'],
                aliases=aliases
            ))
        return categories_result

    def get_all_categories(self) -> List[Dict]:
        """Возвращает справочник категорий."""
        return self._categories

    def get_category(self, category_name: str) -> Category:
        """Возвращает категорию по одному из её алиасов."""
        finded = None
        other_category = None
        for category in self._categories:
            if category.codename == "other":
                other_category = category
            for alias in category.aliases:
                if category_name in alias:
                    finded = category
        if not finded:
            finded = other_category
        return finded

    def get_categ_name(self, result):
        res = []
        for tup in result:
            lst = list(tup)
            res.append(lst)
        for lst in res:
            for category in self._categories:
                if category.codename == lst[0]:
                    lst[0] = category.name.capitalize()
        resul = ''
        for lst in res:
            lst[1] = str(lst[1])
            spis = ' — '.join(lst)
            resul += spis + ' руб.' + '\n'
        return resul
