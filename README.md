# Сервис для планирования маршрута атомного ледокола по Северному морскому пути

## Описание

Сервис позволяет планировать маршрут атомного ледокола по Северному морскому пути. 
На основе динамических данных о ледовой обстановке на СМП и фиксированного графа переходов судов (типовых маршрутов судов) по СМП
предлагается решить задачу оптимального движения транспортных судов по

## Структура проекта

- `data/` - данные о ледовой обстановке на СМП
- `docs/` - документация
- `app/` - исходный код АПИ для взаимодействия с сервисом и работы с celery
- `notebooks/` - исходный код алгоритмов и исследований
- `scripts/` - дополнительные скрипты
- `tests/` - тесты

## Инструкция по установке

TODO: написать инструкцию по установке (В процессе)
Для запуска проекта необходимо содержимое каталога `deploy`, каталог `app` и файл `requirements.txt` разместить в корневой директории, далее следовать инструкциям из файла README.md находящегося в каталоге deploy


## Описание методов АПИ и примеры взаимодействия с ними


#### POST /users/login

**Описание**: Авторизация пользователя.

**Параметры запроса**: Объект, содержащий логин и пароль пользователя.

**Формат ответа**: Объект, содержащий токен авторизации.

**Пример запроса**:

```
POST /users/login
```

```json
{
  "login": "user",
  "password": "password"
}
```


**Пример ответа**:

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwibG9naW4iOiJ1c2VyIn0.1"
}
```

#### GET /nsi/edges

**Описание**: Получение списка всех ребер графа (взаимосвязей между портами).

**Параметры запроса**: Нет.

**Формат ответа**: Массив объектов, каждый из которых представляет ребро графа.

**Пример запроса**:

```
GET /nsi/edges
```

**Пример ответа**:

```json
[
  {
    "id": 1,
    "start_point": "Point A",
    "end_point": "Point B",
    "weight": 10
  },
  {
    "id": 2,
    "start_point": "Point B",
    "end_point": "Point C",
    "weight": 5
  }
]
```

#### GET /nsi/points

**Описание**: Получение списка всех точек графа (портов).

**Параметры запроса**: Нет.

**Формат ответа**: Массив объектов, каждый из которых представляет точку графа.

**Пример запроса**:

```
GET /nsi/points
```

**Пример ответа**:

```json
[
  {
    "id": 1,
    "name": "Point A",
    "coordinates": [55.7558, 37.6176]
  },
  {
    "id": 2,
    "name": "Point B",
    "coordinates": [59.9343, 30.3351]
  }
]
```

#### GET /orders

**Описание**: Получение списка всех заявок на перевозку судов.

**Параметры запроса**: start - дата начала периода, end - дата окончания периода.

**Формат ответа**: Массив объектов, каждый из которых представляет заявку на перевозку.

**Пример запроса**:

```
GET /orders
```

**Пример ответа**:

```json
[
    {
        "id": 1,
        "name_ship": "ДЮК II",
        "class_ship": "Arc 5",
        "speed": 15.0,
        "point_start": "Новый порт",
        "point_end": "Рейд Мурманска",
        "date_start_swim": "2022-03-01",
        "status": 0
    },
    {
        "id": 2,
        "name_ship": "САРМАТ",
        "class_ship": "Arc 4",
        "speed": 15.0,
        "point_start": "Сабетта",
        "point_end": "Архангельск",
        "date_start_swim": "2022-03-02",
        "status": 0
    }
]
```

#### POST /orders/add

**Описание**: Добавление новой заявки на перевозку судов.

**Параметры запроса**: Объект, содержащий данные о заявке на перевозку.

**Формат ответа**: Объект, содержащий данные о добавленной заявке на перевозку.

**Пример запроса**:

```
GET /orders/add
```

```json
{
    "name_ship": "ДЮК II - test2",
    "class_ship": "Arc 5",
    "speed": 15.0,
    "point_start": "Новый порт",
    "point_end": "Рейд Мурманска",
    "date_start_swim": "2022-03-01"
}
```

**Пример ответа**:

```json
{
    "status": "ok",
    "order_id": 58
}
```

#### POST /orders/delete

**Описание**: Удаление заявки на перевозку судов.

**Параметры запроса**: id - идентификатор заявки на перевозку.

**Формат ответа**: Объект, содержащий статус операции.

**Пример запроса**:

```
GET /orders/delete
```

```json
{
    "id": 58
}
```

**Пример ответа**:

```json
{
    "status": "ok"
}
```

#### GET /icebreakers

**Описание**: Получение списка всех ледоколов.

**Параметры запроса**: Нет.

**Формат ответа**: Массив объектов, каждый из которых представляет ледокол.

**Пример запроса**:

```
GET /icebreakers
```

**Пример ответа**:

```json
[
    {
        "id": 1,
        "name_icebreaker": "50 лет Победы",
        "speed": 22.0,
        "class_icebreaker": "Arc 9",
        "start_position": "Пролив Лонга"
    },
    {
        "id": 2,
        "name_icebreaker": "Ямал",
        "speed": 21.0,
        "class_icebreaker": "Arc 9",
        "start_position": "Рейд Мурманска"
    }
]
```

#### POST /icebreakers/add

**Описание**: Добавление нового ледокола.

**Параметры запроса**: Объект, содержащий данные о ледоколе.

**Формат ответа**: Объект, содержащий данные о добавленном ледоколе.

**Пример запроса**:

```
POST /icebreakers/add
```

```json
{
    "name_icebreaker": "Вайгач - test",
    "speed": 18.5,
    "class_icebreaker": "Arc 9",
    "start_position": "Победа месторождение"
}
```

**Пример ответа**:

```json
{
    "status": "ok",
    "icebreaker_id": 6
}
```

#### POST /icebreakers/delete

**Описание**: Удаление ледокола.

**Параметры запроса**: id - идентификатор ледокола.

**Формат ответа**: Объект, содержащий статус операции.

**Пример запроса**:

```
POST /icebreakers/delete
```

```json
{
    "id": 58
}
```

**Пример ответа**:

```json
{
    "status": "ok"
}
```

## POST /calculate/task/run

**Описание**: Запуск задачи расчета маршрута.

**Параметры запроса**: Объект, содержащий идентификаторы ледокола и заявки на перевозку.

**Формат ответа**: Объект, содержащий идентификатор задачи.

**Пример запроса**:

**Пример запроса**:

```
POST /calculate/task/run
```

TODO: добавить пример запроса

**Пример ответа**:

```json
{
  "task_id": "746812c1-c27a-48cb-b693-11bb6a0a620b"
}
```

## GET /calculate/task/{task_id}

**Описание**: Получение информации о задаче расчета маршрута.

**Параметры запроса**: task_id - идентификатор задачи.

**Формат ответа**: Объект, содержащий информацию о задаче.

**Пример запроса**:

```
GET /calculate/task/746812c1-c27a-48cb-b693-11bb6a0a620b
```

**Пример ответа**:

```json
{
    "task_id": "746812c1-c27a-48cb-b693-11bb6a0a620b",
    "status": "SUCCESS",
    "result": 0.15
}
```




