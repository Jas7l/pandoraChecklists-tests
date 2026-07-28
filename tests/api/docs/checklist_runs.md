## 1. Паспорт проверки — Checklist Runs

| Поле | Значение |
| --- | --- |
| Проект | pandoraChecklists |
| Функциональность | `checklist-runs` (прогоны чек-листов) |
| Окружение | `Dev / Test / Staging` |
| Версия API / Commit | _тег/commit_ |
| Base URL | `http://localhost:8081` |
| Документация | Swagger `/swagger/index.html` |
| Роль / способ авторизации | Токенов нет. Внутренняя сеть |
| Проба живости | `GET /ping` → `200`, пустое тело |
| Итог | `Pass / Fail / Blocked / Not Run` |

## 2. Объём проверки — Checklist Runs

| Что проверяется | Что не проверяется / ограничения |
| --- | -- |
| Создание прогона чек-листа (`POST /checklist-runs`) | |
| Получение списка прогонов (`GET /checklist-runs`) | |
| Получение прогона по ID (`GET /checklist-runs?run_id=`) | |
| Получение прогонов по machine_id (`GET /checklist-runs?machine_id=`) | |
| Получение прогонов по employee_id (`GET /checklist-runs?employee_id=`) | |
| Получение прогонов по checklist_id (`GET /checklist-runs?checklist_id=`) | |
| Получение прогонов по result_status (`GET /checklist-runs?result_status=`) | |
| Фильтрация по дате (`GET /checklist-runs?date_from=&date_to=`) | |
| Валидация обязательных полей (`checklist_id`, `employee_badge`, `tasks`) | |
| Валидация внешних ключей (`checklist_id`, `employee_badge`, `task_id`) | |
| Валидация статусов (`ok`, `failed`) | |
| Обновление статуса станка после прогона | |
| Обработка ошибок (`400`, `404`) | |
| Пагинация (`limit`, `offset`) | |

### Инварианты контракта (проверять в каждом кейсе)

- **Источник истины — HTTP-статус.** В JSON нет полей `response_code` / `error_code`.
- **Тело ответа:** успех с данными → `200` + массив объектов; создание → `201` + объект.
- **Пагинация:** параметры `limit` (дефолт 0, макс 500) и `offset` (дефолт 0).

## 3. Endpoint-ы — Checklist Runs

| ID | Метод | Endpoint | Назначение | Приоритет | Статус |
| --- | --- | --- | --- | --- | --- |
| API-01 | `GET` | `/api/v1/checklist-runs` | Получить список прогонов | `High` | `Pass` |
| API-02 | `GET` | `/api/v1/checklist-runs?run_id=` | Получить прогон по ID | `High` | `Pass` |
| API-03 | `GET` | `/api/v1/checklist-runs?machine_id=` | Получить прогоны по станку | `High` | `Pass` |
| API-04 | `GET` | `/api/v1/checklist-runs?employee_id=` | Получить прогоны по сотруднику | `High` | `Pass` |
| API-05 | `GET` | `/api/v1/checklist-runs?checklist_id=` | Получить прогоны по чек-листу | `High` | `Pass` |
| API-06 | `GET` | `/api/v1/checklist-runs?result_status=` | Получить прогоны по статусу | `High` | `Pass` |
| API-07 | `GET` | `/api/v1/checklist-runs?date_from=&date_to=` | Получить прогоны по дате | `High` | `Pass` |
| API-08 | `POST` | `/api/v1/checklist-runs` | Создать прогон чек-листа | `High` | `Pass` |

## 4. Предусловия и данные — Checklist Runs

### Предусловия

- Окружение доступно: `GET /ping` → `200`.
- В БД существует хотя бы один прогон чек-листа (получается динамически через API).
- В БД существует сотрудник для получения badge.
- Для тестов создаются: зона, станок, копия чек-листа (автоматически очищаются).
- Для тестов используются реальные данные, полученные из системы.

### Тестовые данные — Checklist Runs

| Название | Значение | Где используется | Примечание |
|----------|----------|------------------|------------|
| Run ID (существующий) | Динамически из API | TC-002, TC-012, TC-013 | Получается через GET /checklist-runs |
| Run Machine ID (существующий) | Динамически из API | TC-004 | Получается из первого прогона |
| Run Employee ID (существующий) | Динамически из API | TC-006 | Получается из первого прогона |
| Run Checklist ID (существующий) | Динамически из API | TC-008 | Получается из первого прогона |
| Run Result Status (существующий) | Динамически из API | TC-010 | Получается из первого прогона |
| Run Started At (существующий) | Динамически из API | TC-012, TC-013 | Получается из первого прогона |
| Employee Badge | Динамически из API | TC-014, TC-015, TC-016, TC-017, TC-018, TC-019, TC-020, TC-021 | Получается из первого сотрудника |
| Employee ID | Динамически из API | TC-006, TC-007 | Получается из первого сотрудника |
| Checklist ID (скопированный) | Динамически из API | TC-014, TC-015, TC-016, TC-017, TC-018, TC-019, TC-020, TC-021 | Копия существующего чек-листа |
| Checklist Task IDs | Динамически из API | TC-014, TC-015, TC-016, TC-017, TC-018, TC-019, TC-020, TC-021 | Задачи скопированного чек-листа |
| Created Machine ID | Динамически из API | TC-014, TC-021 | Создается в setup |
| Area ID | Динамически из API | TC-014, TC-021 | Создается в setup |
| Run ID (несуществующий) | `9999999` | TC-003, TC-005, TC-007, TC-009, TC-011 | Не существует в БД |
| Badge (несуществующий) | `88888888` | TC-015 | Не существует в БД |
| Status (невалидный) | `invalid_status` | TC-011 | Невалидный статус |
| Limit | `10` | TC-001 | Лимит для пагинации |
| Offset | `0` | TC-001 | Смещение для пагинации |

## 5. Тест-кейсы — Checklist Runs

| ID | Endpoint | Сценарий | Тип | Шаги / запрос | Ожидаемый результат | Фактический результат | Статус | Доказательства |
|-----|----------|----------|-----|---------------|----------------------|-----------------------|--------|----------------|
| TC-001 | `GET /checklist-runs` | Получение списка прогонов | `Positive` | GET с параметрами `limit=10&offset=0` | `200` + массив объектов; структура содержит `run_id`, `checklist_id`, `machine_id`, `employee`, `result_status`, `tasks`, `started_at`, `finished_at` | Совпадает с ожидаемым | `Pass` | |
| TC-002 | `GET /checklist-runs?run_id=` | Получение прогона по ID | `Positive` | GET с `run_id` из test_data | `200` + массив с одним объектом; `run_id` соответствует | Совпадает с ожидаемым | `Pass` | |
| TC-003 | `GET /checklist-runs?run_id=` | Получение по несуществующему ID | `Negative` | GET с `run_id: 9999999` | `200` + пустой массив `[]` | Совпадает с ожидаемым | `Pass` | |
| TC-004 | `GET /checklist-runs?machine_id=` | Получение прогонов по machine_id | `Positive` | GET с `machine_id` из test_data | `200` + массив объектов; у всех `machine_id` равен переданному | Совпадает с ожидаемым | `Pass` | |
| TC-005 | `GET /checklist-runs?machine_id=` | Получение по несуществующему machine_id | `Negative` | GET с `machine_id: 9999999` | `200` + пустой массив `[]` | Совпадает с ожидаемым | `Pass` | |
| TC-006 | `GET /checklist-runs?employee_id=` | Получение прогонов по employee_id | `Positive` | GET с `employee_id` из test_data | `200` + массив объектов; у всех `started_by_employee_id` равен переданному | Совпадает с ожидаемым | `Pass` | |
| TC-007 | `GET /checklist-runs?employee_id=` | Получение по несуществующему employee_id | `Negative` | GET с `employee_id: 9999999` | `200` + пустой массив `[]` | Совпадает с ожидаемым | `Pass` | |
| TC-008 | `GET /checklist-runs?checklist_id=` | Получение прогонов по checklist_id | `Positive` | GET с `checklist_id` из test_data | `200` + массив объектов; у всех `checklist_id` равен переданному | Совпадает с ожидаемым | `Pass` | |
| TC-009 | `GET /checklist-runs?checklist_id=` | Получение по несуществующему checklist_id | `Negative` | GET с `checklist_id: 9999999` | `200` + пустой массив `[]` | Совпадает с ожидаемым | `Pass` | |
| TC-010 | `GET /checklist-runs?result_status=` | Получение прогонов по result_status | `Positive` | **Параметризованный тест:** `ok`, `failed` | `200` + массив объектов; у всех `result_status` равен переданному | Совпадает с ожидаемым | `Pass` | |
| TC-011 | `GET /checklist-runs?result_status=` | Получение по невалидному статусу | `Negative` | GET с `result_status: invalid_status` | Должен быть `400` + ошибка валидации | Совпадает с ожидаемым | `Pass` | |
| TC-012 | `GET /checklist-runs?date_from=` | Фильтрация по date_from | `Positive` | GET с `date_from` > даты создания тестового прогона | `200` + массив объектов; тестовый прогон исключен из результатов | Совпадает с ожидаемым | `Pass` | |
| TC-013 | `GET /checklist-runs?date_to=` | Фильтрация по date_to | `Positive` | GET с `date_to` < даты создания тестового прогона | `200` + массив объектов; тестовый прогон исключен из результатов | Совпадает с ожидаемым | `Pass` | |
| TC-014 | `POST /checklist-runs` | Создание прогона со всеми задачами ok | `Positive` | POST с телом: <br/> `{"checklist_id": <id>, "employee_badge": <badge>, "tasks": [{"task_id": <id>, "is_ok": true}, ...]}` | `201` + созданный объект; `result_status: ok`; `status: completed`; статус станка обновлен на `ok` | Совпадает с ожидаемым | `Pass` | |
| TC-015 | `POST /checklist-runs` | Создание с несуществующим employee_badge | `Negative` | POST с `employee_badge: 88888888` | Должен быть `404` + ошибка `employee not found` | Совпадает с ожидаемым | `Pass` | |
| TC-016 | `POST /checklist-runs` | Создание с пропущенной задачей | `Negative` | POST с `tasks` содержащим не все задачи из чек-листа | Должен быть `400` + ошибка валидации | Совпадает с ожидаемым | `Pass` | |
| TC-017 | `POST /checklist-runs` | Создание с дублирующейся задачей | `Negative` | POST с `tasks` содержащим дублирующийся `task_id` | Должен быть `400` + ошибка валидации | Совпадает с ожидаемым | `Pass` | |
| TC-018 | `POST /checklist-runs` | Создание с несуществующей задачей | `Negative` | POST с `tasks` содержащим `task_id: 9999999` | Должен быть `400` + ошибка валидации | Совпадает с ожидаемым | `Pass` | |
| TC-019 | `POST /checklist-runs` | Создание с пропущенным полем is_ok | `Negative` | POST с `tasks` где у одной задачи отсутствует `is_ok` | Должен быть `400` + ошибка валидации | Совпадает с ожидаемым | `Pass` | |
| TC-020 | `POST /checklist-runs` | Создание для неактивного чек-листа | `Negative` | 1. Деактивировать чек-лист <br/> 2. POST с `checklist_id` | Должен быть `400` + ошибка `checklist is not active` | Совпадает с ожидаемым | `Pass` | |
| TC-021 | `POST /checklist-runs` | Создание с failed задачей | `Positive` | POST с `tasks` где одна задача имеет `is_ok: false` | `201` + созданный объект; `result_status: failed`; `status: completed`; статус станка обновлен на `accident` | Совпадает с ожидаемым | `Pass` | |

## 6. Дефекты — Checklist Runs

| ID | Краткое описание | Severity | Endpoint / метод | Шаги воспроизведения | Ожидаемо | Фактически | X-Request-Id | Статус |
|-----|------------------|----------|------------------|----------------------|----------|------------|--------------|--------|
| BUG-001 | Нет выявленных дефектов | - | - | - | - | - | - | - |

## 7. Итог — Checklist Runs

| Статус | Количество |
|--------|------------|
| Pass | 21 |
| Fail | 0 |
