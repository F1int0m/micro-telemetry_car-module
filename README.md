# micro-telemetry_car-module

Проект телеметрии с прошивкой для модуля на шасси. Модуль собирает данные с гироскопа, а потом может выгружать их в
мастер систему для обработки

## Окружение разработки

1. WeMos D1 mini V4.0
2. [Micropython 1.24 для ESP8266](https://docs.micropython.org/en/v1.24.0/esp8266/quickref.html)
3. Python 3.8
4. [Плагин для Pycharm](https://github.com/JetBrains/intellij-micropython) и все что ему нужно для работы

На плату загружается все содержимое папки [src](src)

В папке [service](service) может лежать какой-то отладочный инструментарий, который не нужен в прошивке, но нужен для
локальной разработки/настройки

Лучше создать отдельное окружение под проект и установить зависимости из [requirements.txt](requirements.txt), чтобы без
проблем загружать прошивку на плату

## Концепция

Модуль должен уметь работать в режимах master/slave

- Master

  В этом режиме модуль должен сам создавать точку и поддаваться конфигурации
- Slave

  В этом режиме модуль должен работать основное время. На старте они синхронизирует системное время для повышения
  точности измерений

Независимо от режима модуль должен выставлять 2 эндпоинта:

1. `/info` - в нем он должен отдавать какую-то системную информация и то, как этот модуль можно идентифицировать
2. `/dump` - тут он должен отдать наружу валидный json со списком измерений. Каждое измерение это список из 2 элементов:
   timestamp и значение скорости/ускорения

## Конфигурация

Базовые настройки лежат в файле [base.py](src%2Fconfig%2Fbase.py). Для того чтобы менять их локально и для временной
загрузки в модуль, можно создавать рядом файлик local.py и настроить все переменные так, как это нужно

Более низкоуровневые параметры следует оставлять в начале файлов, в которых они нужны(либо выносить в конфиг, если они
используются в нескольких местах)

## Known issues

1. Не нормальная работа http соединения. Обрывается раньше, чем это ожидает клиент
2. Фильтрация данных с гироскопа на модуле