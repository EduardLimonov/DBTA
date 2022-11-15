# DBTA
 Simple distributed data store

### Описание

Учебный проект

Приложение с графическим интерфейсом, позволяющее выполнить SQL-запрос к таблицам различных баз данных разных серверов (только MySQL).

Допускается выполнение JOIN между таблицами баз данных с разных серверов (по равенству произвольных атрибутов). 
Этот механизм был реализован путем создания временных Federated tables для выполнения запроса.

Пользователь имеет возможность выполнить SQL-запрос с добавлением указанных JOIN, применить сортировки и фильтры (с отношениями равенства или неравенства атрибута другому атрибуту или произвольному значению).

Приложение использует базу данных для хранения схем доступных баз данных зарегистрированных пользователем серверов.
Эти схемы используются для того, чтобы вывести пользователю в графическом интерфейсе соответствующий список доступных элементов (серверов, БД, таблиц, атрибутов).

Также приложение хранит в json текущие состояния - введенные фильтры и сортировочные формы для различных таблиц (сохранение введенных фильтров и форм происходит при выполнении запроса).



### Запуск 
Для запуска необходимо отредактировать файл resource/metadata_storage, введя в него информацию о том, где должна быть размещена база данных метаданных приложения по форме:

- IP сервера;
- имя пользователя;
- пароль;
- порт;
- имя базы данных метаданных.

Если базы данных метаданных еще не существует, то она будет создана.

Приложение разработано на Python 3.10, использованы дополнительные библиотеки PyQt5, mysql-connector.
