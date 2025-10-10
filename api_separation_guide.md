# OneFlow.AI - API Separation Guide
## Руководство по разделению API

---

## 🎯 Обзор архитектуры API

OneFlow.AI использует **раздельные API ключи** для каждого типа контента, что обеспечивает:
- ✅ Гибкость в выборе провайдеров
- ✅ Независимое управление затратами
- ✅ Возможность использовать разные аккаунты
- ✅ Оптимизацию стоимости для каждого типа контента

---

## 📋 Детальное разделение по типам контента

### 1️⃣ ТЕКСТ (TEXT)

#### Доступные провайдеры:

**OpenAI GPT**
- **API ключ**: `openai`
- **Модели**: 
  - `gpt-3.5-turbo` (быстрая, дешевая)
  - `gpt-4` (мощная, дорогая)
  - `gpt-4-turbo` (быстрая версия GPT-4)
- **Стоимость**: $0.0005 - $0.03 за 1K токенов
- **Получить ключ**: https://platform.openai.com/api-keys
- **Формат ключа**: `sk-...` (48 символов)

**Anthropic Claude**
- **API ключ**: `anthropic`
- **Модели**:
  - `claude-3-haiku` (быстрая)
  - `claude-3-sonnet` (балансированная)
  - `claude-3-opus` (мощная)
- **Стоимость**: $0.0008 - $0.015 за 1K токенов
- **Получить ключ**: https://console.anthropic.com/settings/keys
- **Формат ключа**: `sk-ant-...`

**Пример конфигурации**:
```json
{
  "openai": "sk-proj-abc123...",
  "anthropic": "sk-ant-xyz789..."
}
```

---

### 2️⃣ ИЗОБРАЖЕНИЯ (IMAGE)

#### Доступные провайдеры:

**Stability AI (Stable Diffusion)**
- **API ключ**: `stability`
- **Модели**:
  - `stable-diffusion-xl-1024-v1-0`
  - `stable-diffusion-v2-1`
- **Стоимость**: ~$0.01 за изображение (система кредитов)
- **Получить ключ**: https://platform.stability.ai/account/keys
- **Формат ключа**: `sk-...`

**OpenAI DALL-E**
- **API ключ**: `openai` (тот же, что для текста!)
- **Модели**:
  - `dall-e-3` (1024x1024, высокое качество)
  - `dall-e-2` (512x512, дешевле)
- **Стоимость**: $0.04 - $0.12 за изображение
- **Получить ключ**: https://platform.openai.com/api-keys

**Пример конфигурации**:
```json
{
  "openai": "sk-proj-abc123...",    // Для DALL-E
  "stability": "sk-stability-xyz..."  // Для Stable Diffusion
}
```

**💡 Совет**: Один ключ OpenAI работает и для текста, и для изображений!

---

### 3️⃣ АУДИО (AUDIO)

#### Доступные провайдеры:

**ElevenLabs (Text-to-Speech)**
- **API ключ**: `elevenlabs`
- **Модели**:
  - `eleven_monolingual_v1` (английский)
  - `eleven_multilingual_v2` (29 языков)
- **Стоимость**: 
  - Free tier: 10,000 символов/месяц
  - Paid: от $5/месяц за 30,000 символов
- **Получить ключ**: https://elevenlabs.io/app/settings/api-keys
- **Формат ключа**: 32 символа (hex)

**Пример конфигурации**:
```json
{
  "elevenlabs": "a1b2c3d4e5f6..."
}
```

---

### 4️⃣ ВИДЕО (VIDEO)

#### Доступные провайдеры:

**Runway ML**
- **API ключ**: `runway`
- **Модели**:
  - `gen-2` (text-to-video, image-to-video)
  - `gen-1` (video-to-video)
- **Стоимость**: Система кредитов, ~$0.05/секунда
- **Получить ключ**: https://runwayml.com/account
- **Статус**: ⚠️ API в разработке (заглушка в коде)

**Пример конфигурации**:
```json
{
  "runway": "rwml_..."
}
```

---

## 🔧 Полная конфигурация .api_keys.json

### Минимальная конфигурация (только текст)

```json
{
  "openai": "sk-proj-abc123..."
}
```

### Рекомендуемая конфигурация

```json
{
  "openai": "sk-proj-abc123...",      // Текст + Изображения
  "stability": "sk-stability-xyz...", // Изображения (дешевле)
  "elevenlabs": "a1b2c3d4..."         // Аудио
}
```

### Максимальная конфигурация

```json
{
  "openai": "sk-proj-abc123...",      // GPT + DALL-E
  "anthropic": "sk-ant-xyz789...",    // Claude (альтернатива GPT)
  "stability": "sk-stability-def...", // Stable Diffusion
  "elevenlabs": "a1b2c3d4e5f6...",    // Text-to-Speech
  "runway": "rwml_ghijkl..."          // Video generation
}
```

---

## 💰 Оптимизация затрат

### Стратегия 1: Минимальные затраты
```json
{
  "openai": "sk-..."  // Только GPT-3.5-turbo
}
```
- Текст: GPT-3.5-turbo ($0.0005/1K)
- Изображения: DALL-E 2 ($0.016/image)
- **Итого**: ~$10/месяц для легкого использования

### Стратегия 2: Качество + Экономия
```json
{
  "anthropic": "sk-ant-...",  // Claude Haiku для текста
  "stability": "sk-..."       // Stable Diffusion для изображений
}
```
- Текст: Claude Haiku ($0.0008/1K)
- Изображения: Stable Diffusion ($0.01/image)
- **Итого**: ~$15/месяц для среднего использования

### Стратегия 3: Максимальное качество
```json
{
  "openai": "sk-...",      // GPT-4 для текста
  "stability": "sk-...",   // SDXL для изображений
  "elevenlabs": "..."      // Премиум аудио
}
```
- Текст: GPT-4 ($0.03/1K)
- Изображения: SDXL ($0.01/image)
- Аудио: ElevenLabs Premium
- **Итого**: $50+/месяц для активного использования

---

## 🛡️ Безопасность API ключей

### ✅ Правильно:

1. **Храните в .api_keys.json**
```bash
chmod 600 .api_keys.json  # Только владелец может читать
```

2. **Добавьте в .gitignore**
```bash
echo ".api_keys.json" >> .gitignore
```

3. **Используйте переменные окружения (production)**
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### ❌ Неправильно:

- ❌ Коммит ключей в Git
- ❌ Публикация ключей в коде
- ❌ Использование production ключей в dev
- ❌ Передача ключей в URL параметрах

---

## 📊 Мониторинг использования

### Проверка конфигурации

```python
from enhanced_api_manager import EnhancedAPIManager

manager = EnhancedAPIManager()

# Показать все провайдеры
print(manager.get_configuration_summary())

# Проверить доступность по типу
text_providers = manager.get_available_providers_by_type(ContentType.TEXT)
print(f"Available text providers: {len(text_providers)}")

# Валидация
validation = manager.validate_configuration()
print(f"Configuration valid: {validation['valid']}")
```

### CLI команды

```bash
# Проверить статус API
python -m src.cli api-status

# Список провайдеров по типу
python -m src.cli list-providers --type text

# Проверить конкретный ключ
python -c "from src.api_keys import get_key_manager; km = get_key_manager(); print(km.get_masked_key('openai'))"
```

---

## 🔄 Переключение между провайдерами

### Автоматическое переключение

OneFlow.AI автоматически выбирает лучшего доступного провайдера:

```python
from src.main import OneFlowAI

system = OneFlowAI(use_real_api=True)

# Автоматически выберет: OpenAI или Anthropic (что доступно)
result = system.process_request('gpt', 'Hello world')

# Автоматически выберет: Stability AI или DALL-E
result = system.process_request('image', 'A sunset')
```

### Ручной выбор провайдера

```python
from real_api_integration import RealGPTProvider

# Явно указать OpenAI
gpt_openai = RealGPTProvider(preferred_api='openai')
response = gpt_openai('Hello', model='gpt-4')

# Явно указать Anthropic
gpt_anthropic = RealGPTProvider(preferred_api='anthropic')
response = gpt_anthropic('Hello', model='claude-3-opus')
```

---

## 🚀 Быстрый старт

### Шаг 1: Получите минимум один ключ
```bash
# Зарегистрируйтесь на OpenAI
https://platform.openai.com/signup

# Создайте API ключ
https://platform.openai.com/api-keys
```

### Шаг 2: Настройте ключ
```bash
# Интерактивная настройка
python setup_keys.py

# Или вручную создайте .api_keys.json
echo '{"openai": "sk-your-key"}' > .api_keys.json
chmod 600 .api_keys.json
```

### Шаг 3: Проверьте работу
```bash
# Demo режим (без ключей)
python -m src.main --demo

# Реальные API (с ключами)
python -m src.main
# Выберите "y" для real API
```

---

## 📞 Поддержка провайдеров

| Провайдер | Статус | Документация |
|-----------|--------|--------------|
| OpenAI GPT | ✅ Полностью | https://platform.openai.com/docs |
| Anthropic Claude | ✅ Полностью | https://docs.anthropic.com |
| Stability AI | ✅ Полностью | https://platform.stability.ai/docs |
| OpenAI DALL-E | ✅ Полностью | https://platform.openai.com/docs/guides/images |
| ElevenLabs | ✅ Полностью | https://elevenlabs.io/docs |
| Runway ML | ⚠️ В разработке | https://docs.runwayml.com |

---

## ❓ FAQ

### Можно ли использовать один ключ OpenAI для текста и изображений?
Да! Один API ключ OpenAI работает для GPT и DALL-E.

### Нужно ли настраивать все ключи сразу?
Нет. Минимум нужен один текстовый провайдер (OpenAI или Anthropic).

### Как узнать, какие ключи настроены?
```python
from src.api_keys import get_key_manager
km = get_key_manager()
print(km.list_providers())
```

### Можно ли изменить приоритет провайдеров?
Да, в коде `real_api_integration.py` измените `preferred_api` параметр.

### Что делать, если ключ не работает?
1. Проверьте формат ключа
2. Убедитесь, что есть кредиты на счету
3. Проверьте rate limits провайдера
4. Посмотрите логи ошибок

---

## 🎓 Дополнительные ресурсы

- **Installation Guide**: См. `installation_guide.md`
- **Developer Guide**: См. `developer_guide.md`
- **Examples**: См. `examples.md`
- **Quick Start**: См. `quickstart.md`

---

**Готово! Теперь вы знаете всё о разделении API в OneFlow.AI! 🎉**