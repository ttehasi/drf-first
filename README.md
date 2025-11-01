Обязательные зависимости:

| Tool                                       | Description                                                            |
|--------------------------------------------|------------------------------------------------------------------------|
| [uv](https://docs.astral.sh/uv/)           | "An extremely fast Python package and project manager, written in Rust" |
| [OS Linux](https://www.linux.org/)               | "Семейство Unix-подобных операционных систем на базе ядра Linux"                           |
| [make](https://www.gnu.org/software/make/)               | "Инструмент для автоматизации процессов преобразования файлов"                           |
| [Git](https://git-scm.com/)               | "Git is a free and open source distributed version control system designed to handle everything from small to very large projects with speed and efficiency."                           |


Для начала нужно скопировать репозиторий себе на локальную машину. Для этого откройте терминал и пропишите команду:
~~~
git clone git@github.com:ttehasi/drf-first.git
~~~

Далее переходим в рабочую дерикторию:
~~~
cd drf-first
~~~

Переходим в дерикторию /web:
~~~
cd web
~~~

После чего необходимо установить зависимости. Прописываем команду:
~~~
uv sunc
~~~

После создаем локальную бд и наполняем её:
~~~
make loaddb
~~~

#### Поздравляю! Почти все готово.
После утановки нужно запустить сервер.
Находясь в рабочей дериктории выполните команду:
~~~
make run
~~~

### После этого преходим в браузере по адресу `http://localhost:8000` и авторизируемся. (Перед этим создав суперпользователя)

### Хотите поднять docker-compose, то нужно в директории drf-first/nginx создать конфигурационный файл nginx.conf под ваши нужны, и прописать из главной папки проекта:
~~~
docker-compose up -d
~~~


