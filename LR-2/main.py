import json
import csv
import yaml
import requests
from abc import ABC, abstractmethod
from typing import Dict, Any, List


class Component(ABC):

    @abstractmethod
    def get_data(self) -> List[Dict[str, Any]]:
        pass


class CBCCurrencyComponent(Component):

    def __init__(self) -> None:
        self._url = "https://www.cbr-xml-daily.ru/daily_json.js"

    def get_data(self) -> List[Dict[str, Any]]:

        try:
            response = requests.get(self._url)
            response.raise_for_status()
            data = response.json()

            valute_data = []
            # Чистим данные, получаем только курсы валют
            for code, info in data["Valute"].items():
                info["CharCode"] = code 
                valute_data.append(info)
            return valute_data
        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
            return []


class Decorator(Component):

    def __init__(self, component: Component) -> None:
        self._component = component

    @property
    def component(self) -> Component:

        return self._component

    def get_data(self) -> Any:
        return self._component.get_data()

    @abstractmethod
    def save_to_file(self, filename: str) -> None:
        pass


class YamlDecorator(Decorator):

    def get_data(self) -> str:
        data = self.component.get_data()
        return yaml.dump(data, allow_unicode=True)

    def save_to_file(self, filename: str) -> None:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(self.get_data())
        print(f"Данные успешно сохранены в {filename}")

class JSONDecorator(Decorator):

    def get_data(self):
        data = self.component.get_data()
        return json.dumps(data, indent=4)
    
    def save_to_file(self, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(self.get_data())
        print(f"Данные успешно сохранены в {filename}")

class CsvDecorator(Decorator):

    def get_data(self) -> List[Dict[str, Any]]:
        return self.component.get_data()

    def save_to_file(self, filename: str) -> None:
        data = self.get_data()
        if not data:
            return

        keys = data[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(data)
        print(f"Данные успешно сохранены в {filename}")


if __name__ == "__main__":

    cb_data = CBCCurrencyComponent()

    yaml_ver = YamlDecorator(cb_data)
    print("--- YAML DATA SAMPLE ---")
    print(yaml_ver.get_data()[:200] + "...") 
    yaml_ver.save_to_file("currencies.yaml")

    json_ver = JSONDecorator(cb_data)
    json_ver.save_to_file('currencies.json')

    csv_ver = CsvDecorator(cb_data)
    csv_ver.save_to_file("currencies.csv")