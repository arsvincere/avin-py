# Проблемы которые решает программа

## Нет денег
Всю жизнь только и вертишься чтобы денег заработать, а есть и другие дела которыми бы хотелось заняться. Пусть роботы торгуют, а люди живут.

## Торчать за монитором следя за графиками
Сидеть на бирже от открытия до закрытия тяжело физически, интеллектуально и особенно эмоционально. 

## Гипероптимизм в оценке стратегий
Надежда на то что сделка окажется выигрышной, конгинитивные искажения при ручном просмотре исторических графиков и мысленной прикидке как бы задуманная стратегия работала. Мозг обычно выхватывает места на графике где стратегия бы сработала, и пропускает ложные входы.

## Импульсивная торговля
Нарушение правил торговой системы

## Следить 3 и более активами одновременно
На одном мониторе много графиков и стаканов не разместишь, и ресурсов мозга не хватит для их отслеживания.

## Долго сводить отчеты
Вручную в Exel

## Данных мало
Ограничение на количество отображаемых баров в TradingView

## Один брокер Тинькофф
С остальными вообще невозможно работать

## Не написать стратегию
Приходится торговать ручками даже если уже понятно что надо делать

## Desktop app
Самый хороший терминал у тинькова, но он браузерный - тормозной.



# Возможности программы

## Кнопка бабло
Нажал - и система зарабатывает деньги. Только вот механику работы после нажатия кнопки придется написать самому.

## Поиск стратегий
Инструменты для поиска паттернов, выявления закономерностей, анализа данных и извлечения из них информации.

## Работа по расписанию
Возможность настроить работу системы автономно по расписанию.

## Уведомления
Присылает уведомления, отчеты в телеграмм или на почту

## Бэктестер
Простой бэктестер. Возможно форк bt или backtrader. С построением кривой капиталла. С возможностью протестировать группу стратегий в одном портфеле.

## Песочница
Проверка работы стратегии реал тайм на бумажном счете.

## Риск менеджер
- Настройки допустимых рисков на одну сделку, день, неделю, месяц. Порог отключения стратегии, и остановки системы в целом.
- Риск менеджер прикреплен к каждому отдельному трейдеру и содержит настройки для него.

## Портфолио менеджер
- Следит за всей системой в целом. За всеми трейдерами, которые могут работать на разных счетах, разных биржах, и с совершенной разными стратегиями, и дейтрейдерские и долгосрочные.

## Сканер
- Следит за аномалиями на рынке. Присылает уведомления.
- Может отправлять информацию об аномалии системе, которая может отреагировать предопределенными способами - скорректировать торговлю, остановить, или наоборот начать торговать агрессивно.

## Авто отчеты
- Построение отчетов с графиками и сводными таблицами.
- Просмотр внутри приложения.
- Экспорт в PDF

## Исторические данные
- Загрузка с различных источников
- Преобразование таймфреймов
- Своя сборка даты по стакану 
- Своя сборка даты по потоку сделок

## Коннекторы
- Модули прокладки между внутренней системой и API конкретных брокеров. 
- Реализует единый интерфейс для всех подключений.

## API for traders
- Классы облегчающие написание стратегий. 
- Высокоуровневые абстракции - бар, график, стакан, акция, облигация, экстремумы, тренды и тп.

## GUI
- Десктопный графический интерфейс на PyQt

## CLI
- Возможность работы с системой консоль. Ручная правка конфигов (настроек теста, песочницы, трейдеров)
- Запуск тестов и торговли через консоль.
- Интерфейс с отображением информации о работе системы, аналогичный lazygit




chart widget
    axis datetime
    axis price
    cursor
    item или итемс...
    конфиг. мб ТОМЛ с цветами и грузим его
    или глобальный конфиг с цветами с разделом чарт???


Journal - для хранения архива сделок?



