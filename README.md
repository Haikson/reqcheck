Скрипт проверяет, надо ли обновлять пакеты твоего проекта из requirements.txt

1. Установи необходимые пакеты
2. Создай файл config.json по подобию config.tmpl.json
3. Запусти

```
python checker.py [out_file]
```

- Если запускать без опции, выведет json в консоль
- Для сохранения в файл смотрит на расширение выходного файла
- Поддерживает форматы json и csv