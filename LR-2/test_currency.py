
import unittest
from unittest.mock import Mock, patch

try:
    from main import *
except:
    from main import *


class TestMinimal(unittest.TestCase):    
    def test_01_is_classes_exists(self):
        """Тест: классы созданы"""
        self.assertTrue('CBCCurrencyComponent' in globals())
        self.assertTrue('YamlDecorator' in globals())
        self.assertTrue('JSONDecorator' in globals())
        self.assertTrue('CsvDecorator' in globals())
    
    @patch('main.requests.get')
    def test_02_can_get_dollar(self, mock_get):
        """Тест: можно получить доллар"""
        fake_response = Mock()
        fake_response.json.return_value = {
            "Valute": {
                "USD": {
                    "CharCode": "USD",
                    "Value": 75.50,
                    "Name": "Доллар"
                }
            }
        }
        mock_get.return_value = fake_response
        c = CBCCurrencyComponent()
        data = c.get_data()
        
        self.assertEqual(data[0]['CharCode'], 'USD')
        self.assertEqual(data[0]['Value'], 75.50)
    
    def test_03(self):
        """Тест: YAML декоратор работает?"""
        class TestComponent:
            def get_data(self):
                return [{'test': 'data', 'value': 123}]
        
        d = YamlDecorator(TestComponent())
        result = d.get_data()

        self.assertIsInstance(result, str)

if __name__ == '__main__':
    print("Запускаем простые тесты...")
    unittest.main()