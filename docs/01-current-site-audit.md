# Аудит текущего сайта SkySend

Дата снятия: 10 сентября 2026. Источник: https://skysend.ru/. Это аудит содержимого источника, а не подтверждение актуальности коммерческих условий.

## Охват и метод

Сохранены 125 HTML-страниц: все уникальные URL главного меню, главная, основные связанные материалы, 11 страниц каталога загрузок и две подробные карточки терминалов. Каждый ответ получил HTTP 200 при проверке. Это не означает, что все функции страницы или внешние файлы работают. По каждому URL сохранены HTML, SHA-256, заголовки, точный основной DOM-текст, блоки с ID, изображения, ссылки, файлы и формы. Повторяющиеся меню и футер исключены из основного текста. Текст, встроенный в картинки, отдельно исследуется визуально в комплекте ассетов.

- Машинный источник: `data/source-pages.json` и копия `evidence/skysend/pages.json`.
- Читаемый точный текст каждой страницы: `evidence/skysend/text/`.
- Карта переходов: `data/migration-map.csv`.
- Все 122 карточки скачивания: `data/downloads-source.json`.
- Динамический публичный справочник: `data/providers-source.json`, 600 записей, 13 категорий.
- Проверка служебных ссылок: `data/service-link-checks.json`.

В `blocks` исходная пунктуация, регистр и факты сохранены. `text` разворачивает DOM в строки, поэтому слова внутри ссылок могут оказаться на разных строках. Поля `decoded_emails` восстановлены из доступных HTML data-атрибутов защиты от спама. Формы не отправлялись.

## Основные блоки старой главной

| Порядок | Содержимое источника | Решение |
|---|---|---|
| 1 | Шапка: логотип, телефон, вход/регистрация, большое многоуровневое меню | Компактная шапка; «Программы» → «ПО» |
| 2 | Автопереключаемый слайдер: `po5.jpg`, акция `0_first.jpg` → `76-sweetstock.html`, поставщики `banf.png`, `2.jpg` | Убрать слайдер и промо. Функциональный смысл ПО и поставщиков использовать в самостоятельных секциях |
| 3 | «ВЫСОКИЕ СТАВКИ ВОЗНАГРАЖДЕНИЯ», «ЭКОНОМИЯ 50% НА ОБСЛУЖИВАНИИ», «НЕТ УДЕРЖАНИЙ И СКРЫТЫХ КОМИССИЙ» | Не переносить неподтверждённые обещания в hero |
| 4 | Шесть входов: «Платежным агентам», «Провайдерам услуг», «Поставщикам товаров», «Торговым сетям», «Представителям», «Шлюзовикам» | Сохранить шесть аудиторий; заменить стоковые картинки предметным визуалом |
| 5 | Новости 15.05.2024, 24.02.2024, 10.10.2022, 29.09.2022 | Убрать с главной. Непромо-материалы сохранить датированным архивом |
| 6 | «Продажа товаров и услуг», «Реклама продукции и акций», «Режим инфокиоска» | Сохранить торговые и информационные функции ПО; рекламу и акции удалить |
| 7 | «Изменение цветов и фона», «Смена положений и форм элементов», «Перестроение логики работы ПО» | Секция настройки интерфейса с реальными скриншотами |
| 8 | «Загрузка справочника товаров», «Формирование заказов», «Оплата заказов» | Секция заказа товаров с тремя связанными экранами |
| 9 | Реклама: «Видео», «SMS», «Баннер», «Чек» | Полностью исключить |
| 10 | Футер: другие сайты группы, статьи, загрузки, контакты | Краткий навигационный футер, проверенные ссылки и контакты |

Главная опирается на большой объём текста внутри растровых баннеров. Полный редизайн нельзя делать только по HTML-тексту. В новом сайте заголовки и подписи нужно вынести в живой текст, а визуал собирать из исходных изображений продуктов и интерфейсов.

## Структура источника

Верхний уровень: ПО ALLVEND, Автопробег, Партнерам, Купить, Преимущества, Программы, Скачать, О системе. Партнёрские страницы разбиты на множество коротких статей; одни и те же механизмы повторяются в «Преимуществах», ПО и страницах разных аудиторий.

Новая структура консолидирует эти материалы, но сохраняет адреса через карту 301 и устойчивые якоря. Промо без смыслового эквивалента получает 410, без редиректа на главную.

## Исключения и конфликтующие данные

1. Полностью исключить `/autorally.html`, `/about/news/76-sweetstock.html`, `/partners/advertisers/*`, промо-баннеры и рекламные CTA. В ALLVEND исключить рекламные модули, блоки бесплатных услуг и ценовые примеры. В загрузках скрыть рекламные предложения/договоры из нового публичного каталога.
2. «Более 5000» есть в title, страницах агентов, шлюза и ALLVEND. Публичный endpoint `/providers.php` вернул 600 записей услуг и 13 категорий. Эти величины могут описывать разный охват. Не подменять 5000 числом 600 и не объявлять 5000 проверенным на 2026. Steam в полученном справочнике не найден; логотип в старом баннере не подтверждает текущую доступность оплаты.
3. Главная и общий футер: 350049, Краснодар, Монтажников, 1/4. Контакты: Краснодар, Красных Партизан, 218; внутри указан индекс 352500, а во всплывающем контакте 350049. До проверки использовать «Адрес офиса уточняйте по телефону».
4. Шапка и контакты: +7 (800) 555-25-36; POS и часть старых статей поддержки: +7 (800) 200-25-36. Для новой версии использовать номер из текущей шапки, конфликт не замалчивать.
5. `/about/geografiy.html`: `sales@inf-sys.ru`, `support@inf-sys.ru`. `/about/feedback.html`: `support@isg.dev`, Telegram `@infsysgroup`. Новый контактный слой должен явно выбрать источник; не смешивать адреса случайным образом.
6. На старом сайте встречаются гарантии 50% снижения расходов, 20% роста доходов, «самое высокое вознаграждение в стране», 1000 транзакций/сек (в других статьях 10 000), «ни единого сбоя за 11 лет», «5 степеней криптозащиты», старые цены и сроки. В новом тексте использовать конкретные механизмы: удалённое управление, обновления, справочники, XML, отчётность. Числа и абсолютные утверждения не превращать в актуальные обещания.
7. Новость 10.10.2022 сообщает о прекращении поддержки ПО 5-го поколения 10.12.2020. В загрузках одновременно есть демообраз v. 5.45 из `/old/`, РМА 5.24, POS 1.1. Не называть их автоматически последними версиями.
8. В карточке «Установка и эксплуатация РМА Linux» в каталоге нет ссылки. `Play Market`/`App Store` в тексте FINGER не гарантируют наличие актуального приложения: магазинные CTA проверять отдельно.
9. Регистрационный URL `https://cluster.skysend.ru:6716/agent.php` не прошёл проверку цепочки TLS в среде аудита (`unable to get local issuer certificate`). Не утверждать, что регистрация не работает везде; интеграцию нужно проверить в целевой среде. Пароли и формы не отправлялись.
10. `map.php` содержит Yandex Maps и поиск `skysend`, а не выгрузку координат всех терминалов. Нельзя рисовать выдуманные точки сети. Ссылки логотипов провайдеров идут по HTTP на порт 6721, встречаются пустые src и некорректные сайты `http://`, `http://нет`. Нужны локальные ассеты и валидация URL.
11. Биографии руководства, вакансии, реквизиты, банковские сведения и контакты дилеров сохранены как исходные сведения; актуальность не установлена. Их нельзя обновлять догадками. Юридические документы не редактировать стилистически.

## Дополнительная проверка структуры и динамических функций

- Четыре ответа HTTP 200 содержат soft 404: профили Беляевой, Лифановой, Стародуба и `/component/k2/item/16.html?Itemid=520` («Торговым сетям»). Страница `/trading.html` не содержит основного текста. Розничное направление нового сайта составлено по функциональному описанию `/allvend.html`.
- Справочник `/providers.php` доступен: 600 записей и 13 категорий сохранены локально. В новой странице `/providers/` допустим локальный поиск именно по этому снимку с датой. Не обещать живое обновление или полноту всех 5000 услуг.
- Прочитана фактическая форма `/exit.php?ml=1`: ссылка регистрации `https://cluster.skysend.ru:6716/#/`, действие входа формы POST `https://control.skysend.ru:6710`. Старый `/agent.php` остаётся в скрытом исходном блоке, но не выбран для новой CTA. Запросы без отключения TLS дали ошибку цепочки сертификата регистрации и ошибку DNS кабинета в среде аудита. Это зафиксированные ограничения проверки, не утверждение о глобальной недоступности. Новая `/connect/` содержит контактный fallback.
- Две карточки оборудования проверены отдельно. Beauty II: 50 см ширина, 145 см высота, 75 кг; глубина отсутствует. Simple: 50×144×38 см, 80 кг. Обе: 220 В, 50 Гц, 120 Вт, сенсорная панель 17″. У Simple в исходной комплектации есть б/у позиции и расхождение модема 3G/GPRS. Точная копия: `data/equipment-content.json`.
- Полная карта `data/migration-map.csv` содержит 147 адресов: 125 снятых страниц и дополнительные обнаруженные ссылки карточек товаров, сопоставленные строкам категорий. Дополнительные карточки компонентов не считались просмотренными детальными страницами.

## Текст внутри изображений главной

Визуальная расшифровка сделана по скачанным оригиналам; это не OCR догадка. Контактный лист: `assets/contact-sheets/legacy-banners-review.jpg`. Отдельная машинная запись: `data/home-image-transcripts.json`.

| Изображение | Видимый текст | Перенос |
|---|---|---|
| `/images/Sky/slaider/banf.png` | «БОЛЕЕ 5 000 ПРОВАЙДЕРОВ УСЛУГ» | Сохранить исходный смысл; актуальность числа отдельно не подтверждена |
| `/images/banners/po5.jpg` | «ТРАНСФОРМАЦИЯ ТЕРМИНАЛЬНОГО БИЗНЕСА»; «УНИВЕРСАЛЬНОЕ ПРОГРАММНОЕ ОБЕСПЕЧЕНИЕ ДЛЯ ПЛАТЕЖНЫХ И ИНФОРМАЦИОННЫХ ТЕРМИНАЛОВ» | Функциональный заголовок ПО сохранить; лозунг убрать |
| Тот же `po5.jpg` | «ИЗМЕНЕНИЕ ДИЗАЙНА • ПРОДАЖА ТОВАРОВ И УСЛУГ • РЕЖИМ ИНФОКИОСКА • ОПЛАТА НАЛИЧНЫМИ И КАРТОЙ • ПОКАЗ РЕКЛАМЫ • ПОЛНОЕ УДАЛЕННОЕ УПРАВЛЕНИЕ» | Функции раскрыть через реальные экраны; рекламу исключить; способы оплаты не расширять сверх исходника |
| `/images/banners/best_term.jpeg` | «ЛУЧШЕЕ РЕШЕНИЕ ДЛЯ СИСТЕМ САМООБСЛУЖИВАНИЯ» | Оценочный лозунг исключить |
| `/images/banners/design.jpeg` | «СМЕНА ДИЗАЙНА ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ ПОД ВАШ СТИЛЬ» | Сохранить функцию настройки интерфейса |
| `/images/banners/pomarket.jpeg` | «АВТОМАТИЗАЦИЯ ЗАКАЗА И ОПЛАТЫ ПРОДУКЦИИ» | Сохранить в торговом сценарии |
| `/images/banners/terminal_pr.jpeg` | «ТРАНСЛЯЦИЯ РЕКЛАМЫ ВАШИХ УСЛУГ И ПРОДУКЦИИ» | Исключить целиком |
| `/images/banners/v.png` | «ЗАБЕРИ СВОЙ ПОДАРОК» | Исключить целиком |

## Точные тексты ключевых страниц

Ниже приведён исходный основной текст. Это материал для сопоставления; рекламные обещания и старые сведения не являются утверждённой копией нового сайта. Полный текст всех остальных страниц находится по ссылкам в реестре ниже.

### SkySend – система приема платежей, предоставляющая возможность совершения оплат в пользу более 5 000 поставщиков услуг

Источник: https://skysend.ru/

```text
ВЫСОКИЕ СТАВКИ ВОЗНАГРАЖДЕНИЯ
ВЫСОКИЕ СТАВКИ
/
ЭКОНОМИЯ 50% НА ОБСЛУЖИВАНИИ
ЭКОНОМИЯ 50%
/
НЕТ УДЕРЖАНИЙ И СКРЫТЫХ КОМИССИЙ
НЕТ УДЕРЖАНИЙ
Платежным агентам
Провайдерам услуг
Поставщикам товаров
Торговым сетям
Представителям
Шлюзовикам
Новости
15 Май 2024
Компании исполняется 18 лет!
Уважаемые друзья! Сегодня 15 мая 2024 года Группа компаний «Информ-Системы» отмечает свое...
Читать дальше...
15 Май 2024
Компании исполняется 18 лет!
Уважаемые друзья! Сегодня 15 мая 2024 года Группа компаний «Информ-Системы» отмечает свое...
Читать дальше...
24 Февраль 2024
Подключение платежных терминалов к системе SkySend!
Дорогие друзья! Переводите платежные терминалы на систему SkySend, это просто, быстро и надежно....
Читать дальше...
24 Февраль 2024
Подключение платежных терминалов к системе SkySend!
Дорогие друзья! Переводите платежные терминалы на систему SkySend, это просто, быстро и надежно....
Читать дальше...
10 Октябрь 2022
Поддержка старых версий ПО
Уважаемые партнеры! В связи с тем, что обеспечение работоспособности программного обеспечения 5-го...
Читать дальше...
10 Октябрь 2022
Поддержка старых версий ПО
Уважаемые партнеры! В связи с тем, что обеспечение работоспособности программного обеспечения 5-го...
Читать дальше...
29 Сентябрь 2022
Бизнес-миссия ГК «Информ-Системы» в Азербайджан
Уважаемые друзья! ГК «Информ-Системы» приняла участие в бизнес-миссии в Азербайджан,...
Читать дальше...
29 Сентябрь 2022
Бизнес-миссия ГК «Информ-Системы» в Азербайджан
Уважаемые друзья! ГК «Информ-Системы» приняла участие в бизнес-миссии в Азербайджан,...
Читать дальше...
Продажа товаров и услуг
Реклама продукции и акций
Режим инфокиоска
Изменение цветов и фона
Смена положений и форм элементов
Перестроение логики работы ПО
Загрузка справочника товаров
Формирование заказов
Оплата заказов
Видео
SMS
Баннер
Чек
```

### Платежным агентам

Источник: https://skysend.ru/partners/agent/information.html

```text
При работе с системой SkySend Ваши расходы на содержание терминальной
сети и точек приема платежей сократятся на
50%
, а доходы вырастут на
20%.
SkySend гарантирует Вам самое высокое вознаграждение в стране, отсутствие скрытых комиссий, более 5 000 поставщиков услуг, доступных к оплате, а также стабильную работу терминалов и круглосуточную поддержку Ваших плательщиков.
ПреИмущества системы SkySend
Стабильная
работа
Снижение
Расходов
Удаленное
Управление
Рост
Доходов
Уникальные
Инновации
Система SkySend предлагает Вам
Перевести
Терминалы
Купить
Терминалы
Операторские
Точки
Установить
Сканер
```

### Стабильная работа

Источник: https://skysend.ru/partners/agent/stable-work.html

```text
Стабильная работа терминалов
Терминалы SkySend работают на базе операционной системы FastSYS (построена на базе ядра ОС Linux).
Система FastSYS содержит широкий набор автоматик терминала, которые обеспечивают стабильную работу терминалов без
сбоев, зависаний и других болезней терминалов, работающих на ОС Windows.
Среди автоматик системы FastSyS выделяют :
автоматическое устранение ошибок купюроприемника, модема и фискального регистратора
удаленные бинарные обновления программного обеспечения
система анализа работы устройств терминала
система автоматической отладки управляющего программного обеспечения
Быстрый запуск
Для запуска терминала в работу достаточно вставить flash-накопитель, содержащий в себе бесплатную операционную систему FastSYS и ПО платежного терминала, в свободный разъем материнской платы, ввести пароли для регистрации терминала и скачать справочники кнопок оплаты услуг.
Запуск терминала SkySend в работу занимает несколько минут!
Надежность
Операционная система терминалов SkySend работают с flash-накопителя, рабочий диапазон температур составляет от -40°C до +60°C, благодаря чему терминалы отлично работают и в жару, и в холод.
Быстрая настройка
Нет необходимости устанавливать операционную систему, устанавливать и конфигурировать программное обеспечение платежного терминала, скачивать драйвера устройств и проводить несколько часов около терминала.
Благодаря работе с системой
SkySend
заботы Агентов по наладке работы
терминалов
просто не возникают!
Стать Агентом SkySend Вы можете, заполнив анкету регистрации посредством
online-формы
, либо связавшись с менеджером.
www.skysend.ru +7 (800) 555-25-36
```

### Удаленное управление

Источник: https://skysend.ru/partners/agent/remote-control.html

```text
Удалённое управление
Полное управление
Агентам системы SkySend предоставляется личный интернет-кабинет, посредством которого, не выходя из дома, они могут осуществлять полное удаленное управление своими терминалами.
Не нужно ждать
Интернет-кабинет содержит в себе широкий функционал, благодаря которому Агент может решать все возникающие при работе вопросы без обращения в службу поддержки и ожидания обработки его обращений менеджерами.
Возможности личного кабинета Агента:
настройка комиссий, наценок, любимых номеров, отправки уведомлений;
управление автоматиками терминалов;
осуществление контроля работы терминалов, инкассаций;
отслеживание платежей и финансовых движений в системе SkySend;
определение порядка положения кнопок оплаты услуг на терминалах;
регистрация терминалов и т.д.
Несмотря на обилие возможностей, личный кабинет Агента прост в управлении и интуитивно понятен для пользователя любого уровня. Кроме того, Личный кабинет Агента содержит раздел со справочной информацией, описанием работы функционала кабинета и инструкциями по работе.
При работе терминалов с системой
SkySend
Агентам нет необходимости ехать к терминалам и обращаться к менеджерам системы для организации работы по приему платежей, настройки и контроля корректности работы терминалов.
Стать Агентом SkySend Вы можете, заполнив анкету регистрации посредством
online-формы
, либо связавшись с менеджером.
load...
```

### Провайдерам услуг

Источник: https://skysend.ru/partners/providers/information.html

```text
Получите дополнительные точки оплаты Ваших услуг
СкайСенд предлагает Вам поместить кнопку оплаты Ваших услуг на платёжных терминалах системы SkySend. Вы сможете получить дополнительный сервис, который позволит максимально упростить и значительно увеличить число мест приёма платежей.
ПреИмущества системы SkySend
Сеть
приема
платежей
Бесплатное
подключение
защита
данных
высокая
скорость
автоматизация
отчетности
Система SkySend предлагает Вам
ПОдключение к
skYsend
подключение к
finger
ключевое
партнерство
разместить
терминалы
```

### Поставщикам товаров

Источник: https://skysend.ru/partners/suppliers/information.html

```text
Общая информация
SkyMarket
– модуль заказа товаров на терминалах системы
SkySend
и в онлайн-кошельке
Finger
. Участвуя в Проекте
SkyMarket
, Вы быстро и без затрат организуете сеть из нескольких тысяч мест продаж Ваших товаров, расположенную в ряде регионов страны, а также разместите Ваши товары для продажи в онлайн-кошельке
Finger
, работающем на территории всей страны!
ПреИмущества системы SkySend
Бесплатное
подключение
новый
рынок сбыта
быстрый
запуск
рост
доходов
справочник
товаров
Система SkySend предлагает Вам
ПОдключение к
skYsend
подключение к
finger
работа в
кабинете
интеграция
по XML
```

### Представителям

Источник: https://skysend.ru/partners/representatives/predstavitelyam.html

```text
Общая информация
Представитель системы SkySend может наладить работу направлений SkySend в своем регионе и получать ежемесячный высокий доход от их работы. Став Представителем SkySend, Вы получите множество готовых решений для развития системы SkySend в Вашем регионе, благодаря чему сможете подключать новых участников к системе SkySend и получать высокие доходы от их работы.
ПреИмущества системы SkySend
статьи
доходов
дилерские
скидки
открытое
партнерство
эксклюзивность
в регионе
подключение
участников
Система SkySend предлагает Вам
касса в
регионе
точки расчетов
отпечатком
освоение
направлений
```

### Шлюзовикам

Источник: https://skysend.ru/partners/gateway/information.html

```text
Общая информация
При работе с системой SkySend Вы получаете самое высокое вознаграждение в стране, отсутствие скрытых комиссий,
более 5000 поставщиков услуг, доступных к оплате, высокую скорость проведения платежей, круглосуточную службу технической поддержки и возможность работы по xml-протоколу.
ПреИмущества системы SkySend
Высокое
вознагрождение
круглосуточная
поддержка
xml
протокол
высокая
скорость
быстрое
начало работы
Система SkySend предлагает Вам
подключить
провайдеров
купить
терминалы
операторские
точки
перевести
терминалы
```

### Программы

Источник: https://skysend.ru/program.html

```text
Программное обеспечение и загрузки
ПО платежного терминала FastPay
Подключение по XML-протоколу
ПО приема платежей для кассира
Прием платежей для смартфонов
ПО для POS-терминала
Приложение FINGER для смартфонов
```

### Терминальное ПО

Источник: https://skysend.ru/program/terminal-software.html

```text
УНИВЕРСАЛЬНОЕ ПРОГРАММНОЕ ОБЕСПЕЧЕНИЕ
для платежных и информационных терминалов
Для запуска терминала в работу с системой SkySend нет необходимости устанавливать операционную систему, программное обеспечение и драйвера устройств, проводя у терминала несколько часов..
ПО терминалов SkySend предустанавливается на любой flash-накопитель и обладает встроенным модулем автоматического обнаружения подключаемых переферийных устройств и настройки их работы.
Для запуска терминала в работу Вам остается лишь вставить flash-накопитель, уже содержащий в себе ПО терминала, в свободный слот материнской платы и ввести регистрационные данные.
Благодаря такому подходу запуск терминала системы SkySend занимает
несколько минут
!
Участники системы SkySend могут самостоятельно программировать flash-накопители для запуска терминалов в работу, установив на свой рабочий компьютер или ноутбук прошивочную систему. Для простоты настройки рекомендуем обратиться к инструкции по организации прошивочной системы.
Система поддерживает множество видов накопителей, обращаем Ваше внимание, если вы планируете прошивать накопители формата USB FLASH, для стабильной работы мы настоятельно рекомендуем использовать только проверенные flash накопители из данного перечня.
Предварительно ознакомиться с возможностями терминального ПО системы SkySend Вы можете скачав демонстрационную версию ПО терминала в виде образа виртуальной машины VMware. Для запуска вам потребуется
VMware Workstation Player
.
```

### РМА Windows / linux

Источник: https://skysend.ru/program/rma-pc.html

```text
ПО приема платежей для кассира
Прием платежей в системе SkySend можно организовать в любом магазине, ларьке, кинотеатре, сети салонов связи или гостиниц и в любых других местах быстро и без лишних затрат.
Система SkySend предоставляет программу приема платежей (рабочее место Агента – РМА) на персональный компьютер (стационарный, либо ноутбук) под управлением ОС Windows, ОС Linux.
Для запуска рабочего места Агента в работу достаточно скачать приложение, ввести пароли для его регистрации в системе SkySend и скачать справочники кнопок оплаты услуг.
Запуск РМА SkySend в работу занимает несколько минут!
```

### РМА Android

Источник: https://skysend.ru/program/rma-android.html

```text
ПО приема платежей для смартфонов
Прием платежей в системе SkySend можно осуществлять в любое время и любом месте!
Система SkySend предоставляет партнерам приложение для приема платежей с планшета или смартфона под управлением ОС Android.
Для запуска приложения для ОС Android достаточно скачать приложение на устройство, ввести пароли для его регистрации в системе SkySend и скачать справочники кнопок оплаты услуг.
Запуск в работу приложения приема платежей для планшета/смартфона занимает несколько минут!
```

### XML шлюз

Источник: https://skysend.ru/program/xml-gateway.html

```text
Подключение по XML-протоколу
Агенты SkySend могут осуществлять работу по приему платежей посредством XML-протокола.
В случае если у Агента есть собственная предпроцессинговая система, то организовать прием платежей в пользу Провайдеров SkySend можно посредством ее интеграции с системой SkySend по XML-протоколу.
При работе по XML-протоколу Агент полностью автоматизирует работу с системой SkySend, автоматически получая информацию о Провайдерах, технических и финансовых условиях их оплаты и отправляя информацию о совершаемых платежах.
Для интеграции с Системой SkySend по XML-протоколу рекомендуем ознакомиться с
описанием протокола SkyTransact
```

### ПО для POS-терминала

Источник: https://skysend.ru/program/software-for-pos-terminal.html

```text
Программное обеспечение для POS-терминала
Прием платежей в системе SkySend можно организовать посредством POS-терминала.
POS-терминалы идеально подходят для организации приёма платежей в магазинах, киосках и других торговых точках.
Они отличаются небольшими габаритными размерами, отсутствием зависимости от постоянных источников электропитания и проводного интернета (за счет наличия встроенной аккумуляторной батареи и GPRS-модема).
Система SkySend предоставляет возможность работы с POS-терминалом модели Штрих-Mobile Pay PRO.
Для приема платежей посредством POS-терминала скачайте на компьютер приложение с ПО для POS-терминала и зарегистрируйте устройство в системе SkySend, следуя указаниям мастера настройки.
?
В случае возникновения вопросов по запуску и эксплуатации POS-терминала для приема платежей в Системе SkySend Вы можете связаться с техническим специалистом службы поддержки SkySend по бесплатному телефонному номеру
+7 (800) 200-25-36
```

### Приложение FINGER

Источник: https://skysend.ru/program/finger.html

```text
Приложение FINGER для смартфонов
Онлайн-кошелек Finger –безкомиссионный онлайн-кошелек, который является удобным, эффективным и надежным средством расчетов для современных людей.
Среди основных преимуществ кошелька Finger выделяют:
Отсутствие комиссии за оплату услуг;
Отсутствие платы за содержание счета кошелька;
Простота регистрации и работы;
Высокий уровень безопасности транзакций;
Круглосуточная поддержка пользователей.
Работать с кошельком Finger, Вы можете посредством web-интерфейса по адресу:
www.fingerps.com
, либо установив приложение на планшет или смартфон под управлением ОС Android, в котором сможете круглосуточно осуществлять платежи, создавать и использовать шаблоны платежей, получать выписку по всем движениям средств счета Finger.
Чтобы установить мобильное приложение зайдите в Play Market или в App Store и скачайте приложение FINGER.
```

### Наши цели

Источник: https://skysend.ru/about/our-goals.html

```text
Наши цели
На сегодняшний день SkySend – система приема платежей, предоставляющая возможность совершения оплат в пользу более 5 000 поставщиков услуг. Техническую часть Системы SkySend обеспечивает самый мощный процессинговый центр в стране, пропускная способность которого составляет более 1 000 транзакций в секунду.
SkySend предлагает множество вариантов партнерства платежным Агентам – платежные терминалы, ПО для кассира, программа для Android, POS-терминал, интеграция по xml-протоколу.
Помимо партнерства с платежными агентами SkySend предлагает сотрудничество Представителям, Провайдерам услуг, Поставщикам товаров, Торговым сетям, Рекламодателям и Рекламным агентствам, при этом ставя перед собой следующие цели:
Партнер SkySend в каждой стране.
На текущий момент система приема платежей SkySend представлена республике Туркменистан (первая система приема платежей в республике) и Республике Белоруссия. Мы ставим перед собой цель в запуске партнеров по развитию направлений деятельности системы SkySend в каждой стране.
Представитель SkySend в каждом регионе России.
На текущий момент Система SkySend представлена в более чем
15 регионах страны
. Мы ставим перед собой цель в запуске в работу официального Представителя SkySend в каждом регионе и переводе на работу с Системой не менее 30% точек приема платежей России.
Прием заказов SkyMarket в каждом городе страны.
На текущий момент протестирован и запущен в работу модуль заказа товаров различных поставщиков
на терминалах
. Мы ставим перед собой цель в добавлении в модуль заказа товаров SkyMarket не менее 20 самых популярных поставщиков товаров в каждом городе страны.
Активные пользователи Finger по всей стране.
На текущий момент кошелек Finger насчитывает 100 тыс. пользователей. Мы ставим перед собой цель в подключении к Finger не менее 30% активных пользователей онлайн-кошельков страны.
Рекламные партнеры SkySend в каждом городе.
Рекламная платформа SkySend обеспечивает возможность трансляции видеороликов на терминалах, отправки смс плательщикам и печати рекламы в чеках. Мы ставим перед собой цель в трансляции рекламы на всей терминальной сети SkySend в постоянном режиме.
```

### Поддержка

Источник: https://skysend.ru/about/feedback.html

```text
Добро пожаловать в службу
поддержки SkySend!
Получайте сведения о продуктах SkySend,
просматривайте руководства в Интернете,
загружайте последние обновления и многое другое.
Делитесь информацией с другими пользователями
SkySend, получайте обслуживание, поддержку и
профессиональные советы специалистов SkySend.
Выберите удобный для вас способ связи с нами для того что бы оставить отзыв или предложение.
Контакты
Telegram:
E-mail:
@
infsysgroup
Форма обратной связи
Отправить
```

## Реестр всех обследованных страниц

| Источник | Заголовок | Точный текст | Статус контента | Новый адрес / действие |
|---|---|---|---|---|
| [/](https://skysend.ru/) | SkySend – система приема платежей, предоставляющая возможность совершения оплат в пользу более 5 000 поставщиков услуг | [TXT](../evidence/skysend/text/home.txt) | source_content | / |
| [/allvend.html](https://skysend.ru/allvend.html) | ПО ALLVEND | [TXT](../evidence/skysend/text/allvend.txt) | source_content | /software/allvend/ |
| [/autorally.html](https://skysend.ru/autorally.html) | Автопробег | [TXT](../evidence/skysend/text/autorally.txt) | source_content | 410 |
| [/partners.html](https://skysend.ru/partners.html) | Партнерам | [TXT](../evidence/skysend/text/partners.txt) | source_content | /partners/ |
| [/partners/agent/information.html](https://skysend.ru/partners/agent/information.html) | Платежным агентам | [TXT](../evidence/skysend/text/partners__agent__information.txt) | source_content | /partners/agents/ |
| [/partners/agent/stable-work.html](https://skysend.ru/partners/agent/stable-work.html) | Стабильная работа | [TXT](../evidence/skysend/text/partners__agent__stable-work.txt) | source_content | /partners/agents/#stable-work |
| [/partners/agent/cost-reduction.html](https://skysend.ru/partners/agent/cost-reduction.html) | Снижение расходов | [TXT](../evidence/skysend/text/partners__agent__cost-reduction.txt) | source_content | /partners/agents/#cost-reduction |
| [/partners/agent/remote-control.html](https://skysend.ru/partners/agent/remote-control.html) | Удаленное управление | [TXT](../evidence/skysend/text/partners__agent__remote-control.txt) | source_content | /partners/agents/#remote-control |
| [/partners/agent/income.html](https://skysend.ru/partners/agent/income.html) | Рост доходов | [TXT](../evidence/skysend/text/partners__agent__income.txt) | source_content | /partners/agents/#income |
| [/partners/agent/innovation.html](https://skysend.ru/partners/agent/innovation.html) | Уникальные инновации | [TXT](../evidence/skysend/text/partners__agent__innovation.txt) | source_content | /partners/agents/#innovation |
| [/partners/agent/transfer-terminal.html](https://skysend.ru/partners/agent/transfer-terminal.html) | Перевести терминалы | [TXT](../evidence/skysend/text/partners__agent__transfer-terminal.txt) | source_content | /partners/agents/#transfer-terminal |
| [/partners/agent/buy-terminals.html](https://skysend.ru/partners/agent/buy-terminals.html) | Купить терминалы | [TXT](../evidence/skysend/text/partners__agent__buy-terminals.txt) | source_content | /partners/agents/#buy-terminals |
| [/partners/agent/rma.html](https://skysend.ru/partners/agent/rma.html) | Операторские точки | [TXT](../evidence/skysend/text/partners__agent__rma.txt) | source_content | /partners/agents/#rma |
| [/partners/agent/fingerprint-scanner.html](https://skysend.ru/partners/agent/fingerprint-scanner.html) | Установить сканер | [TXT](../evidence/skysend/text/partners__agent__fingerprint-scanner.txt) | source_content | /partners/agents/#fingerprint-scanner |
| [/partners/providers/information.html](https://skysend.ru/partners/providers/information.html) | Провайдерам услуг | [TXT](../evidence/skysend/text/partners__providers__information.txt) | source_content | /partners/providers/ |
| [/partners/providers/payment-collection.html](https://skysend.ru/partners/providers/payment-collection.html) | Сеть приема платежей | [TXT](../evidence/skysend/text/partners__providers__payment-collection.txt) | source_content | /partners/providers/#payment-collection |
| [/partners/providers/free-connection.html](https://skysend.ru/partners/providers/free-connection.html) | Бесплатное подключение | [TXT](../evidence/skysend/text/partners__providers__free-connection.txt) | source_content | /partners/providers/#free-connection |
| [/partners/providers/privacy-policy.html](https://skysend.ru/partners/providers/privacy-policy.html) | Защита данных | [TXT](../evidence/skysend/text/partners__providers__privacy-policy.txt) | source_content | /partners/providers/#privacy-policy |
| [/partners/providers/high-speed.html](https://skysend.ru/partners/providers/high-speed.html) | Высокая скорость | [TXT](../evidence/skysend/text/partners__providers__high-speed.txt) | source_content | /partners/providers/#high-speed |
| [/partners/providers/automate-reporting.html](https://skysend.ru/partners/providers/automate-reporting.html) | Автоматизация отчётности | [TXT](../evidence/skysend/text/partners__providers__automate-reporting.txt) | source_content | /partners/providers/#automate-reporting |
| [/partners/providers/connecting-to-skysend.html](https://skysend.ru/partners/providers/connecting-to-skysend.html) | Подключение к SkySend | [TXT](../evidence/skysend/text/partners__providers__connecting-to-skysend.txt) | source_content | /partners/providers/#connecting-to-skysend |
| [/partners/providers/connecting-to-finger.html](https://skysend.ru/partners/providers/connecting-to-finger.html) | Подключение к Finger | [TXT](../evidence/skysend/text/partners__providers__connecting-to-finger.txt) | source_content | /partners/providers/#connecting-to-finger |
| [/partners/providers/partnership.html](https://skysend.ru/partners/providers/partnership.html) | Ключевое партнёрство | [TXT](../evidence/skysend/text/partners__providers__partnership.txt) | source_content | /partners/providers/#partnership |
| [/partners/providers/placing-terminals.html](https://skysend.ru/partners/providers/placing-terminals.html) | Размещение терминалов | [TXT](../evidence/skysend/text/partners__providers__placing-terminals.txt) | source_content | /partners/providers/#placing-terminals |
| [/partners/suppliers/information.html](https://skysend.ru/partners/suppliers/information.html) | Поставщикам товаров | [TXT](../evidence/skysend/text/partners__suppliers__information.txt) | source_content | /partners/suppliers/ |
| [/partners/suppliers/freeconnection.html](https://skysend.ru/partners/suppliers/freeconnection.html) | Бесплатное подключение | [TXT](../evidence/skysend/text/partners__suppliers__freeconnection.txt) | source_content | /partners/suppliers/#freeconnection |
| [/partners/suppliers/sales-network-products.html](https://skysend.ru/partners/suppliers/sales-network-products.html) | Сеть продаж товаров | [TXT](../evidence/skysend/text/partners__suppliers__sales-network-products.txt) | source_content | /partners/suppliers/#sales-network-products |
| [/partners/suppliers/ease-of-interaction.html](https://skysend.ru/partners/suppliers/ease-of-interaction.html) | Простота взаимодействия | [TXT](../evidence/skysend/text/partners__suppliers__ease-of-interaction.txt) | source_content | /partners/suppliers/#ease-of-interaction |
| [/partners/suppliers/increase-sales.html](https://skysend.ru/partners/suppliers/increase-sales.html) | Увеличение продаж | [TXT](../evidence/skysend/text/partners__suppliers__increase-sales.txt) | source_content | /partners/suppliers/#increase-sales |
| [/partners/suppliers/directory-of-products.html](https://skysend.ru/partners/suppliers/directory-of-products.html) | Справочник товаров | [TXT](../evidence/skysend/text/partners__suppliers__directory-of-products.txt) | source_content | /partners/suppliers/#directory-of-products |
| [/partners/suppliers/connectingto-skysend.html](https://skysend.ru/partners/suppliers/connectingto-skysend.html) | Подключение к SkySend | [TXT](../evidence/skysend/text/partners__suppliers__connectingto-skysend.txt) | source_content | /partners/suppliers/#connectingto-skysend |
| [/partners/suppliers/connectingto-finger.html](https://skysend.ru/partners/suppliers/connectingto-finger.html) | Подключение к Finger | [TXT](../evidence/skysend/text/partners__suppliers__connectingto-finger.txt) | source_content | /partners/suppliers/#connectingto-finger |
| [/partners/suppliers/work-in-the-office.html](https://skysend.ru/partners/suppliers/work-in-the-office.html) | Работа в кабинете | [TXT](../evidence/skysend/text/partners__suppliers__work-in-the-office.txt) | source_content | /partners/suppliers/#work-in-the-office |
| [/partners/suppliers/integration-in-xml.html](https://skysend.ru/partners/suppliers/integration-in-xml.html) | Интеграция по XML | [TXT](../evidence/skysend/text/partners__suppliers__integration-in-xml.txt) | source_content | /partners/suppliers/#integration-in-xml |
| [/partners/representatives/predstavitelyam.html](https://skysend.ru/partners/representatives/predstavitelyam.html) | Представителям | [TXT](../evidence/skysend/text/partners__representatives__predstavitelyam.txt) | source_content | /partners/representatives/ |
| [/partners/representatives/items-of-income.html](https://skysend.ru/partners/representatives/items-of-income.html) | Статьи доходов | [TXT](../evidence/skysend/text/partners__representatives__items-of-income.txt) | source_content | /partners/representatives/#items-of-income |
| [/partners/representatives/dealer-discounts.html](https://skysend.ru/partners/representatives/dealer-discounts.html) | Дилерские скидки | [TXT](../evidence/skysend/text/partners__representatives__dealer-discounts.txt) | source_content | /partners/representatives/#dealer-discounts |
| [/partners/representatives/publication-of-information.html](https://skysend.ru/partners/representatives/publication-of-information.html) | Публикация информации | [TXT](../evidence/skysend/text/partners__representatives__publication-of-information.txt) | source_content | /partners/representatives/#publication-of-information |
| [/partners/representatives/exclusivity-in-the-region.html](https://skysend.ru/partners/representatives/exclusivity-in-the-region.html) | Эксклюзивность в регионе | [TXT](../evidence/skysend/text/partners__representatives__exclusivity-in-the-region.txt) | source_content | /partners/representatives/#exclusivity-in-the-region |
| [/partners/representatives/connecting-players.html](https://skysend.ru/partners/representatives/connecting-players.html) | Подключение Участников | [TXT](../evidence/skysend/text/partners__representatives__connecting-players.txt) | source_content | /partners/representatives/#connecting-players |
| [/partners/representatives/cashier-in-the-region.html](https://skysend.ru/partners/representatives/cashier-in-the-region.html) | Касса в регионе | [TXT](../evidence/skysend/text/partners__representatives__cashier-in-the-region.txt) | source_content | /partners/representatives/#cashier-in-the-region |
| [/partners/representatives/running-banks-fps.html](https://skysend.ru/partners/representatives/running-banks-fps.html) | Запуск касс FPS | [TXT](../evidence/skysend/text/partners__representatives__running-banks-fps.txt) | source_content | /partners/representatives/#running-banks-fps |
| [/partners/representatives/mastering-directions.html](https://skysend.ru/partners/representatives/mastering-directions.html) | Освоение направлений | [TXT](../evidence/skysend/text/partners__representatives__mastering-directions.txt) | source_content | /partners/representatives/#mastering-directions |
| [/partners/gateway/information.html](https://skysend.ru/partners/gateway/information.html) | Шлюзовикам | [TXT](../evidence/skysend/text/partners__gateway__information.txt) | source_content | /partners/gateways/ |
| [/partners/gateway/high-reward.html](https://skysend.ru/partners/gateway/high-reward.html) | Высокое вознаграждение | [TXT](../evidence/skysend/text/partners__gateway__high-reward.txt) | source_content | /partners/gateways/#high-reward |
| [/partners/gateway/round-the-clock-support.html](https://skysend.ru/partners/gateway/round-the-clock-support.html) | Круглосуточная поддержка | [TXT](../evidence/skysend/text/partners__gateway__round-the-clock-support.txt) | source_content | /partners/gateways/#round-the-clock-support |
| [/partners/gateway/xml.html](https://skysend.ru/partners/gateway/xml.html) | Xml-протокол | [TXT](../evidence/skysend/text/partners__gateway__xml.txt) | source_content | /partners/gateways/#xml |
| [/partners/gateway/highspeed.html](https://skysend.ru/partners/gateway/highspeed.html) | Высокая скорость | [TXT](../evidence/skysend/text/partners__gateway__highspeed.txt) | source_content | /partners/gateways/#highspeed |
| [/partners/gateway/quick-start.html](https://skysend.ru/partners/gateway/quick-start.html) | Быстрое начало работы | [TXT](../evidence/skysend/text/partners__gateway__quick-start.txt) | source_content | /partners/gateways/#quick-start |
| [/partners/gateway/connect-providers.html](https://skysend.ru/partners/gateway/connect-providers.html) | Подключить провайдеров | [TXT](../evidence/skysend/text/partners__gateway__connect-providers.txt) | source_content | /partners/gateways/#connect-providers |
| [/partners/gateway/buy-terminal.html](https://skysend.ru/partners/gateway/buy-terminal.html) | Купить терминалы | [TXT](../evidence/skysend/text/partners__gateway__buy-terminal.txt) | source_content | /partners/gateways/#buy-terminal |
| [/partners/gateway/operator-point.html](https://skysend.ru/partners/gateway/operator-point.html) | Операторские точки | [TXT](../evidence/skysend/text/partners__gateway__operator-point.txt) | source_content | /partners/gateways/#operator-point |
| [/partners/gateway/translate-terminal.html](https://skysend.ru/partners/gateway/translate-terminal.html) | Перевести терминалы | [TXT](../evidence/skysend/text/partners__gateway__translate-terminal.txt) | source_content | /partners/gateways/#translate-terminal |
| [/partners/advertisers/information.html](https://skysend.ru/partners/advertisers/information.html) | Рекламодателям | [TXT](../evidence/skysend/text/partners__advertisers__information.txt) | source_content | 410 |
| [/partners/advertisers/videoadvertising.html](https://skysend.ru/partners/advertisers/videoadvertising.html) | Видеореклама | [TXT](../evidence/skysend/text/partners__advertisers__videoadvertising.txt) | source_content | 410 |
| [/partners/advertisers/partnerships.html](https://skysend.ru/partners/advertisers/partnerships.html) | Партнерство | [TXT](../evidence/skysend/text/partners__advertisers__partnerships.txt) | source_content | 410 |
| [/partners/advertisers/targeting.html](https://skysend.ru/partners/advertisers/targeting.html) | Таргетинг | [TXT](../evidence/skysend/text/partners__advertisers__targeting.txt) | source_content | 410 |
| [/partners/advertisers/efficiency.html](https://skysend.ru/partners/advertisers/efficiency.html) | Эффективность | [TXT](../evidence/skysend/text/partners__advertisers__efficiency.txt) | source_content | 410 |
| [/partners/advertisers/price.html](https://skysend.ru/partners/advertisers/price.html) | Стоимость рекламы | [TXT](../evidence/skysend/text/partners__advertisers__price.txt) | source_content | 410 |
| [/partners/advertisers/statistics-shows.html](https://skysend.ru/partners/advertisers/statistics-shows.html) | Статистика показов | [TXT](../evidence/skysend/text/partners__advertisers__statistics-shows.txt) | source_content | 410 |
| [/partners/advertisers/advertising-on-the-check.html](https://skysend.ru/partners/advertisers/advertising-on-the-check.html) | Реклама на чеках | [TXT](../evidence/skysend/text/partners__advertisers__advertising-on-the-check.txt) | source_content | 410 |
| [/partners/advertisers/online-sms-delivery.html](https://skysend.ru/partners/advertisers/online-sms-delivery.html) | Онлайн смс-рассылка | [TXT](../evidence/skysend/text/partners__advertisers__online-sms-delivery.txt) | source_content | 410 |
| [/buy.html](https://skysend.ru/buy.html) | Купить | [TXT](../evidence/skysend/text/buy.txt) | source_content | /equipment/ |
| [/buy/payment-terminals.html](https://skysend.ru/buy/payment-terminals.html) | Платежные терминалы | [TXT](../evidence/skysend/text/buy__payment-terminals.txt) | source_content | /equipment/payment-terminals/ |
| [/buy/accessories.html](https://skysend.ru/buy/accessories.html) | Комплектующие терминалов | [TXT](../evidence/skysend/text/buy__accessories.txt) | source_content | /equipment/accessories/ |
| [/buy/accessories/hardware.html](https://skysend.ru/buy/accessories/hardware.html) | Компьютерные комплектующие | [TXT](../evidence/skysend/text/buy__accessories__hardware.txt) | source_content | /equipment/accessories/hardware/ |
| [/buy/accessories/acceptor.html](https://skysend.ru/buy/accessories/acceptor.html) | Купюроприемники | [TXT](../evidence/skysend/text/buy__accessories__acceptor.txt) | source_content | /equipment/accessories/acceptor/ |
| [/buy/accessories/modems.html](https://skysend.ru/buy/accessories/modems.html) | Модемы | [TXT](../evidence/skysend/text/buy__accessories__modems.txt) | source_content | /equipment/accessories/modems/ |
| [/buy/accessories/printers.html](https://skysend.ru/buy/accessories/printers.html) | Принтеры | [TXT](../evidence/skysend/text/buy__accessories__printers.txt) | source_content | /equipment/accessories/printers/ |
| [/buy/accessories/other-parts.html](https://skysend.ru/buy/accessories/other-parts.html) | Прочие комплектующие | [TXT](../evidence/skysend/text/buy__accessories__other-parts.txt) | source_content | /equipment/accessories/other-parts/ |
| [/buy/accessories/touch-screens-and-monitors.html](https://skysend.ru/buy/accessories/touch-screens-and-monitors.html) | Сенсорные Экраны И Мониторы | [TXT](../evidence/skysend/text/buy__accessories__touch-screens-and-monitors.txt) | source_content | /equipment/accessories/touch-screens-and-monitors/ |
| [/buy/accessories/fiscal-registrars.html](https://skysend.ru/buy/accessories/fiscal-registrars.html) | Фискальные регистраторы | [TXT](../evidence/skysend/text/buy__accessories__fiscal-registrars.txt) | source_content | /equipment/accessories/fiscal-registrars/ |
| [/buy/flash-drives.html](https://skysend.ru/buy/flash-drives.html) | Flash накопители | [TXT](../evidence/skysend/text/buy__flash-drives.txt) | source_content | /equipment/flash-drives/ |
| [/buy/fingerprint.html](https://skysend.ru/buy/fingerprint.html) | Сканеры отпечатка | [TXT](../evidence/skysend/text/buy__fingerprint.txt) | source_content | /equipment/fingerprint/ |
| [/buy/fiscal-server.html](https://skysend.ru/buy/fiscal-server.html) | Фискальные серверы | [TXT](../evidence/skysend/text/buy__fiscal-server.txt) | source_content | /equipment/fiscal-server/ |
| [/benefits.html](https://skysend.ru/benefits.html) | Преимущества | [TXT](../evidence/skysend/text/benefits.txt) | source_content | /partners/ |
| [/benefits/highest-award.html](https://skysend.ru/benefits/highest-award.html) | Высокое вознаграждение | [TXT](../evidence/skysend/text/benefits__highest-award.txt) | source_content | /partners/agents/#income |
| [/benefits/lower-costs.html](https://skysend.ru/benefits/lower-costs.html) | Низкие расходы | [TXT](../evidence/skysend/text/benefits__lower-costs.txt) | source_content | /partners/agents/#cost-reduction |
| [/benefits/stable-job.html](https://skysend.ru/benefits/stable-job.html) | Стабильная работа | [TXT](../evidence/skysend/text/benefits__stable-job.txt) | source_content | /partners/agents/#stable-work |
| [/benefits/exclusive-innovations.html](https://skysend.ru/benefits/exclusive-innovations.html) | Уникальные инновации | [TXT](../evidence/skysend/text/benefits__exclusive-innovations.txt) | source_content | /partners/agents/#innovation |
| [/benefits/the-high-speed.html](https://skysend.ru/benefits/the-high-speed.html) | Высокая скорость | [TXT](../evidence/skysend/text/benefits__the-high-speed.txt) | source_content | /partners/gateways/#highspeed |
| [/benefits/protection-of-data.html](https://skysend.ru/benefits/protection-of-data.html) | Защита данных | [TXT](../evidence/skysend/text/benefits__protection-of-data.txt) | source_content | /partners/providers/#privacy-policy |
| [/benefits/online-support.html](https://skysend.ru/benefits/online-support.html) | Круглосуточная поддержка | [TXT](../evidence/skysend/text/benefits__online-support.txt) | source_content | /support/ |
| [/program.html](https://skysend.ru/program.html) | Программы | [TXT](../evidence/skysend/text/program.txt) | source_content | /software/ |
| [/program/terminal-software.html](https://skysend.ru/program/terminal-software.html) | Терминальное ПО | [TXT](../evidence/skysend/text/program__terminal-software.txt) | source_content | /software/terminal/ |
| [/program/rma-pc.html](https://skysend.ru/program/rma-pc.html) | РМА Windows / linux | [TXT](../evidence/skysend/text/program__rma-pc.txt) | source_content | /software/rma-desktop/ |
| [/program/rma-android.html](https://skysend.ru/program/rma-android.html) | РМА Android | [TXT](../evidence/skysend/text/program__rma-android.txt) | source_content | /software/rma-android/ |
| [/program/xml-gateway.html](https://skysend.ru/program/xml-gateway.html) | XML шлюз | [TXT](../evidence/skysend/text/program__xml-gateway.txt) | source_content | /software/xml/ |
| [/program/software-for-pos-terminal.html](https://skysend.ru/program/software-for-pos-terminal.html) | ПО для POS-терминала | [TXT](../evidence/skysend/text/program__software-for-pos-terminal.txt) | source_content | /software/pos/ |
| [/program/finger.html](https://skysend.ru/program/finger.html) | Приложение FINGER | [TXT](../evidence/skysend/text/program__finger.txt) | source_content | /software/finger/ |
| [/download.html](https://skysend.ru/download.html) | Скачать | [TXT](../evidence/skysend/text/download.txt) | source_content | /downloads/ |
| [/about.html](https://skysend.ru/about.html) | О системе | [TXT](../evidence/skysend/text/about.txt) | source_content | /about/ |
| [/about/our-goals.html](https://skysend.ru/about/our-goals.html) | Наши цели | [TXT](../evidence/skysend/text/about__our-goals.txt) | source_content | /about/goals/ |
| [/about/history.html](https://skysend.ru/about/history.html) | История | [TXT](../evidence/skysend/text/about__history.txt) | source_content | /about/history/ |
| [/about/geografiy.html](https://skysend.ru/about/geografiy.html) | Контакты | [TXT](../evidence/skysend/text/about__geografiy.txt) | source_content | /contacts/ |
| [/about/providers.html](https://skysend.ru/about/providers.html) | Провайдеры | [TXT](../evidence/skysend/text/about__providers.txt) | source_content | /providers/ |
| [/about/news.html](https://skysend.ru/about/news.html) | Новости | [TXT](../evidence/skysend/text/about__news.txt) | source_content | /about/news/ |
| [/about/feedback.html](https://skysend.ru/about/feedback.html) | Поддержка | [TXT](../evidence/skysend/text/about__feedback.txt) | source_content | /support/ |
| [/about/leaders.html](https://skysend.ru/about/leaders.html) | Руководство | [TXT](../evidence/skysend/text/about__leaders.txt) | source_content | /about/team/ |
| [/about/leaders/belyaeva-olga-konstantinovna.html](https://skysend.ru/about/leaders/belyaeva-olga-konstantinovna.html) | Беляева Ольга Константиновна | [TXT](../evidence/skysend/text/about__leaders__belyaeva-olga-konstantinovna.txt) | soft_404 | /about/team/ |
| [/about/leaders/lifanova-natalya-vladimirovna.html](https://skysend.ru/about/leaders/lifanova-natalya-vladimirovna.html) | Лифанова Наталья Владимировна | [TXT](../evidence/skysend/text/about__leaders__lifanova-natalya-vladimirovna.txt) | soft_404 | /about/team/ |
| [/about/leaders/stepina-anna-anatolevna.html](https://skysend.ru/about/leaders/stepina-anna-anatolevna.html) | Степина Анна Анатольевна | [TXT](../evidence/skysend/text/about__leaders__stepina-anna-anatolevna.txt) | source_content | /about/team/#stepina-anna-anatolevna |
| [/about/leaders/starodub-igor-vladimirovich.html](https://skysend.ru/about/leaders/starodub-igor-vladimirovich.html) | Стародуб Игорь Владимирович | [TXT](../evidence/skysend/text/about__leaders__starodub-igor-vladimirovich.txt) | soft_404 | /about/team/ |
| [/about/leaders/ignatev-alexey-nikolaevich.html](https://skysend.ru/about/leaders/ignatev-alexey-nikolaevich.html) | Игнатьев Алексей Николаевич | [TXT](../evidence/skysend/text/about__leaders__ignatev-alexey-nikolaevich.txt) | source_content | /about/team/#ignatev-alexey-nikolaevich |
| [/about/jobs.html](https://skysend.ru/about/jobs.html) | Вакансии | [TXT](../evidence/skysend/text/about__jobs.txt) | source_content | /about/careers/ |
| [/trading.html](https://skysend.ru/trading.html) |  | [TXT](../evidence/skysend/text/trading.txt) | empty_main_content | /partners/retail/ |
| [/about/news/76-sweetstock.html](https://skysend.ru/about/news/76-sweetstock.html) | Акция "Сладкие условия" | [TXT](../evidence/skysend/text/about__news__76-sweetstock.txt) | source_content | 410 |
| [/component/k2/item/16.html?Itemid=520](https://skysend.ru/component/k2/item/16.html?Itemid=520) | Система приёма платежей SkySend | [TXT](../evidence/skysend/text/component__k2__item__16__411c1b7a.txt) | soft_404 | /partners/retail/ |
| [/about/news/205-18.html](https://skysend.ru/about/news/205-18.html) | Компании исполняется 18 лет! | [TXT](../evidence/skysend/text/about__news__205-18.txt) | source_content | /about/news/#205-18 |
| [/about/news/203-connecting-terminals.html](https://skysend.ru/about/news/203-connecting-terminals.html) | Подключение платежных терминалов к системе SkySend! | [TXT](../evidence/skysend/text/about__news__203-connecting-terminals.txt) | source_content | 410 |
| [/about/news/202-support-older-versions.html](https://skysend.ru/about/news/202-support-older-versions.html) | Поддержка старых версий ПО | [TXT](../evidence/skysend/text/about__news__202-support-older-versions.txt) | source_content | /about/news/#202-support-older-versions |
| [/about/news/201-business-mission-az.html](https://skysend.ru/about/news/201-business-mission-az.html) | Бизнес-миссия ГК «Информ-Системы» в Азербайджан | [TXT](../evidence/skysend/text/about__news__201-business-mission-az.txt) | source_content | 410 |
| [/pravila-sistemy.html](https://skysend.ru/pravila-sistemy.html) | Правила системы SkySend | [TXT](../evidence/skysend/text/pravila-sistemy.txt) | source_content | /system-rules/ |
| [/download/2.html](https://skysend.ru/download/2.html) | Материалы для скачивания | [TXT](../evidence/skysend/text/download__2.txt) | source_content | /downloads/ |
| [/download/3.html](https://skysend.ru/download/3.html) | Материалы для скачивания | [TXT](../evidence/skysend/text/download__3.txt) | source_content | /downloads/ |
| [/download/4.html](https://skysend.ru/download/4.html) | Материалы для скачивания | [TXT](../evidence/skysend/text/download__4.txt) | source_content | /downloads/ |
| [/download/5.html](https://skysend.ru/download/5.html) | Материалы для скачивания | [TXT](../evidence/skysend/text/download__5.txt) | source_content | /downloads/ |
| [/download/6.html](https://skysend.ru/download/6.html) | Материалы для скачивания | [TXT](../evidence/skysend/text/download__6.txt) | source_content | /downloads/ |
| [/download/7.html](https://skysend.ru/download/7.html) | Материалы для скачивания | [TXT](../evidence/skysend/text/download__7.txt) | source_content | /downloads/ |
| [/download/8.html](https://skysend.ru/download/8.html) | Материалы для скачивания | [TXT](../evidence/skysend/text/download__8.txt) | source_content | /downloads/ |
| [/download/9.html](https://skysend.ru/download/9.html) | Материалы для скачивания | [TXT](../evidence/skysend/text/download__9.txt) | source_content | /downloads/ |
| [/download/10.html](https://skysend.ru/download/10.html) | Материалы для скачивания | [TXT](../evidence/skysend/text/download__10.txt) | source_content | /downloads/ |
| [/download/11.html](https://skysend.ru/download/11.html) | Материалы для скачивания | [TXT](../evidence/skysend/text/download__11.txt) | source_content | /downloads/ |
| [/buy/payment-terminals/fastpay-beauty-1-detail.html](https://skysend.ru/buy/payment-terminals/fastpay-beauty-1-detail.html) | FastPay Beauty II | [TXT](../evidence/skysend/text/fastpay-beauty-ii.txt) | source_content | /equipment/payment-terminals/fastpay-beauty-ii/ |
| [/buy/payment-terminals/fastpay-simple-detail.html](https://skysend.ru/buy/payment-terminals/fastpay-simple-detail.html) | FastPay Simple | [TXT](../evidence/skysend/text/fastpay-simple.txt) | source_content | /equipment/payment-terminals/fastpay-simple/ |
