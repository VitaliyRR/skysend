# SkySend design handoff

Этот репозиторий содержит утверждённую постановку, ассеты и макеты публичного сайта SkySend. Разработка сайта ещё не выполнена.

Перед реализацией прочитайте README.md и docs/07-developer-handoff.md. Тексты брать из data/site-content.json, secondary-content.json, utility-content.json и equipment-content.json. Визуальные связи из data/section-assets.json, тайминги из data/motion-spec.json, токены из assets/design-tokens.css.

Не генерировать рекламные слоганы, подставные интерфейсы, показатели или generic изображения. Акции и промо исключены; подпись раздела только «ПО». Исходники evidence/ и source-with-review/ не являются production public assets.

Не запускать исследовательские crawler/генераторы из scripts/ при обычной сборке frontend: они могут перезаписать проверенный снимок. Финальные документы и JSON/CSV уже исправлены по результатам аудита. Проверка комплекта: python tools/validate_handoff.py.

При дальнейшей разработке сохранять существующие материалы и добавлять frontend отдельно от evidence. Путь /connect/ предусматривает поддержку, если внешние кабинеты недоступны; новый сайт не собирает пароли.
