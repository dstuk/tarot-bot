# Bot Commands Contract: Telegram Tarot Reading Chatbot

**Feature**: 001-telegram-tarot-bot
**Date**: 2025-12-04
**Purpose**: Define Telegram bot command/message contracts and response schemas

## Command Overview

| Command | Type | Purpose | User State Required |
|---------|------|---------|---------------------|
| `/start` | Command | Initialize bot, show welcome + buttons | Any |
| `/help` | Command | Display usage instructions | Any |
| "Ask a question" | Button Callback | Enter question mode | `idle` |
| "Explain my own tarot combination" | Button Callback | Enter card input mode | `idle` |
| `<question text>` | Text Message | Submit question for reading | `awaiting_question` |
| `<card names>` | Text Message | Submit card names for interpretation | `awaiting_cards` |

---

## 1. `/start` Command

### Request
**Type**: Telegram Command
**Trigger**: User sends `/start` or opens bot for first time

```
Command: /start
From: Telegram User (user_id: integer)
```

### Response
**Format**: Text message with inline keyboard buttons
**Language**: Detected from Telegram client locale, defaults to English

#### Response Schema (English)

```
Message Text:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔮 Welcome to Tarot Reading Bot!

I can help you gain insights through Tarot card readings.

Choose an option below to begin:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Inline Keyboard:
┌─────────────────────────────────┐
│      🎴 Ask a question          │
├─────────────────────────────────┤
│  🃏 Explain my own combination  │
└─────────────────────────────────┘
```

#### Response Schema (Russian)

```
Message Text:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔮 Добро пожаловать в Таро бот!

Я могу помочь вам получить ответы через расклад карт Таро.

Выберите опцию ниже, чтобы начать:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Inline Keyboard:
┌─────────────────────────────────┐
│      🎴 Задать вопрос           │
├─────────────────────────────────┤
│  🃏 Объяснить мою комбинацию    │
└─────────────────────────────────┘
```

#### Response Schema (Ukrainian)

```
Message Text:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔮 Ласкаво просимо до Таро бота!

Я можу допомогти вам отримати відповіді через розклад карт Таро.

Оберіть опцію нижче, щоб почати:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Inline Keyboard:
┌─────────────────────────────────┐
│      🎴 Поставити питання       │
├─────────────────────────────────┤
│  🃏 Пояснити мою комбінацію     │
└─────────────────────────────────┘
```

### State Transition
**Before**: Any state
**After**: `idle`

### Technical Details
```python
callback_data:
- Button 1: "action:ask_question"
- Button 2: "action:explain_combination"

Implementation:
async def start_handler(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    language = detect_language_from_locale(update.effective_user.language_code)

    # Reset session to idle
    session_service.set_state(user_id, "idle", language)

    # Send welcome message with buttons
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(get_text("btn_ask_question", language),
                              callback_data="action:ask_question")],
        [InlineKeyboardButton(get_text("btn_explain_combination", language),
                              callback_data="action:explain_combination")]
    ])

    await update.message.reply_text(
        get_text("welcome_message", language),
        reply_markup=keyboard
    )
```

---

## 2. `/help` Command

### Request
**Type**: Telegram Command
**Trigger**: User sends `/help`

```
Command: /help
From: Telegram User (user_id: integer)
```

### Response
**Format**: Text message
**Language**: User's session language (or detected)

#### Response Schema (English)

```
Message Text:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📖 How to Use Tarot Reading Bot

🎴 Ask a Question:
1. Click "Ask a question"
2. Type your question in plain language
3. Receive a 3-card Tarot reading with interpretation

🃏 Explain Your Own Combination:
1. Click "Explain my own tarot combination"
2. Enter your card names (comma-separated)
   Example: "The Fool, The Tower, Three of Cups"
3. Receive an interpretation of your cards

🌍 Languages Supported:
• English
• Русский (Russian)
• Українська (Ukrainian)

Language is detected automatically from your message.

⚠️ Note: Tarot readings are for guidance and entertainment purposes only.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### State Transition
**Before**: Any state (no change)
**After**: Same state (no change)

---

## 3. "Ask a question" Button

### Request
**Type**: Inline Button Callback
**Trigger**: User clicks "Ask a question" button

```
Callback Query:
  callback_data: "action:ask_question"
  from: Telegram User (user_id: integer)
```

### Response
**Format**: Edit message (remove buttons) + send prompt text
**Language**: User's session language

#### Response Schema (English)

```
Message Text:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎴 Ask Your Question

Please type your question in plain language. I will draw three Tarot cards and provide an interpretation.

Examples:
• "Should I change my job?"
• "What can I expect in my relationship?"
• "What do I need to focus on today?"

💬 Type your question below:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### State Transition
**Before**: `idle`
**After**: `awaiting_question`

### Error Handling
If user state is not `idle` (already in another flow):
```
❌ Please complete your current action first, or send /start to restart.
```

---

## 4. "Explain my own tarot combination" Button

### Request
**Type**: Inline Button Callback
**Trigger**: User clicks "Explain my own tarot combination" button

```
Callback Query:
  callback_data: "action:explain_combination"
  from: Telegram User (user_id: integer)
```

### Response
**Format**: Edit message (remove buttons) + send prompt text
**Language**: User's session language

#### Response Schema (English)

```
Message Text:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🃏 Enter Your Card Names

Please list the Tarot cards you've drawn, separated by commas.

Examples:
• "The Fool, The Tower, Three of Cups"
• "Magician, Wheel of Fortune, World"
• "Маг, Колесо Фортуны, Мир" (Russian)

I support card names in English, Russian, and Ukrainian.

💬 Type your card names below:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### State Transition
**Before**: `idle`
**After**: `awaiting_cards`

### Error Handling
Same as "Ask a question" button

---

## 5. Question Text Input

### Request
**Type**: Text Message
**Trigger**: User sends text message while in `awaiting_question` state

```
Message:
  text: <user's question string>
  from: Telegram User (user_id: integer)
State Required: awaiting_question
```

### Response
**Format**: Processing indicator + Reading result
**Language**: Detected from question text

#### Processing Indicator

```
Message Text:
🔮 Drawing cards and interpreting...
```

#### Response Schema (Automated Reading)

```
Message Text:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎴 Your Tarot Reading

Question: "<user's question>"

Cards Drawn:
1️⃣ <Card 1 Name> (Past)
2️⃣ <Card 2 Name> (Present)
3️⃣ <Card 3 Name> (Future)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 Interpretation:

<AI-generated interpretation connecting cards to question>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ This reading is for guidance and entertainment purposes only.

Inline Keyboard:
┌─────────────────────────────────┐
│    🎴 Ask another question      │
├─────────────────────────────────┤
│  🃏 Explain my own combination  │
└─────────────────────────────────┘
```

#### Example (English)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎴 Your Tarot Reading

Question: "Should I change my job?"

Cards Drawn:
1️⃣ The Fool (Past)
2️⃣ The Tower (Present)
3️⃣ Three of Cups (Future)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 Interpretation:

The Fool in the Past position indicates that your current career path began with a sense of adventure and new beginnings. You approached this opportunity with optimism and an open mind, ready for whatever came your way.

The Tower in the Present position suggests that you're experiencing significant disruption or revelation. Your current work situation may feel unstable, or you've had a sudden realization about your career. This is a time of necessary change and transformation.

Three of Cups in the Future position is a very positive sign! It indicates celebration, collaboration, and emotional fulfillment. If you choose to make a career change, you'll find yourself in a supportive environment with positive relationships and shared success.

Overall, the cards suggest that while your current situation feels tumultuous (Tower), making a change could lead to a more fulfilling and collaborative work environment (Three of Cups). Trust the journey that began with The Fool's adventurous spirit.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ This reading is for guidance and entertainment purposes only.

┌─────────────────────────────────┐
│    🎴 Ask another question      │
├─────────────────────────────────┤
│  🃏 Explain my own combination  │
└─────────────────────────────────┘
```

### State Transition
**Before**: `awaiting_question`
**After**: `idle` (after interpretation sent)

### Validation Rules
- Question must not be empty
- Question length: 5-500 characters
- Detect language from question text (not from previous session)

### Error Handling

**Empty or too short question** (<5 chars):
```
❌ Please provide a more detailed question (at least 5 characters).
```

**Too long question** (>500 chars):
```
❌ Please keep your question under 500 characters.
```

**Language detection failure**:
```
❌ Sorry, I couldn't detect the language of your question. Please try asking in English, Russian, or Ukrainian.
```

**AI service error**:
```
❌ Sorry, I encountered an error while generating your reading. Please try again in a moment, or send /start to restart.
```

---

## 6. Card Names Text Input

### Request
**Type**: Text Message
**Trigger**: User sends text message while in `awaiting_cards` state

```
Message:
  text: <card names, comma-separated or natural language>
  from: Telegram User (user_id: integer)
State Required: awaiting_cards
```

### Response
**Format**: Processing indicator + Interpretation result
**Language**: Detected from card names text

#### Processing Indicator

```
Message Text:
🃏 Parsing cards and interpreting...
```

#### Response Schema (Custom Interpretation)

```
Message Text:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🃏 Your Card Combination

Cards:
1️⃣ <Card 1 Name>
2️⃣ <Card 2 Name>
3️⃣ <Card 3 Name>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 Interpretation:

<AI-generated interpretation of the specific card combination>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ This interpretation is for guidance and entertainment purposes only.

Inline Keyboard:
┌─────────────────────────────────┐
│    🎴 Ask a question            │
├─────────────────────────────────┤
│  🃏 Explain another combination │
└─────────────────────────────────┘
```

### State Transition
**Before**: `awaiting_cards`
**After**: `idle` (after interpretation sent)

### Validation Rules
- Input must not be empty
- Must parse at least 1 card successfully
- Maximum 10 cards per input
- Fuzzy matching threshold: 0.8 (80% similarity)

### Error Handling

**No cards recognized**:
```
❌ I couldn't recognize any valid Tarot card names in your message.

Please try again with card names like:
• "The Fool, The Tower, Three of Cups"
• "Маг, Башня, Императрица"

Or send /help for more examples.
```

**Partial recognition** (some cards unrecognized):
```
⚠️ I recognized these cards:
• The Fool
• The Tower

But I couldn't recognize:
• "unparseable input"

Would you like me to interpret the cards I found, or would you like to try again?

Reply with:
• "continue" - Interpret recognized cards
• New card names - Try again
```

**Too many cards** (>10):
```
❌ Please provide 10 or fewer cards. You entered {count} cards.
```

**Duplicate cards**:
```
❌ You've listed the same card multiple times. Please ensure each card appears only once in your reading.
```

---

## 7. Error Responses (General)

### Invalid State
When user sends unexpected input for current state:

```
❌ Sorry, I didn't understand that command.

Send /start to begin a new reading, or /help for usage instructions.
```

### Rate Limiting (5 requests per minute)

```
⏱️ Please wait a moment before sending another request. You can make {remaining} more requests in the next minute.
```

### Service Unavailable

```
❌ The Tarot reading service is temporarily unavailable. Please try again in a few moments.

If the problem persists, contact @support_username.
```

---

## Response Time Requirements

| Operation | Target Response Time | Maximum Acceptable |
|-----------|---------------------|-------------------|
| `/start`, `/help` | <500ms | 1s |
| Button click (state change) | <500ms | 1s |
| Question reading (AI call) | <4s | 5s |
| Card interpretation (AI call) | <4s | 5s |

**Rationale**: Spec SC-005 requires <5s response time for all interactions.

---

## Message Length Constraints

| Message Type | Character Limit | Reason |
|--------------|----------------|---------|
| Interpretation Text | 4000 chars | Telegram limit is 4096, leaving 96 for formatting |
| Question Input | 500 chars | Reasonable limit for question clarity |
| Card Names Input | 500 chars | Sufficient for ~10 card names |

---

## Contract Testing Requirements

### Contract Tests Must Verify:

1. **Command Handlers**:
   - `/start` returns welcome message with 2 buttons
   - `/help` returns help text
   - Buttons trigger correct state transitions

2. **State Machine**:
   - State transitions follow defined FSM
   - Invalid state transitions rejected with error message

3. **Response Schemas**:
   - All required fields present in responses
   - Button callback_data format is correct
   - Message text structure matches specification

4. **Validation Rules**:
   - Empty input rejected
   - Length limits enforced
   - Invalid card names handled gracefully

5. **Error Handling**:
   - Rate limiting returns appropriate message
   - Service errors return user-friendly message
   - Invalid states return helpful guidance

---

## Implementation Notes

### Button Callback Data Format
```
action:<action_name>

Examples:
- action:ask_question
- action:explain_combination
```

### Language Detection Priority
1. Detect from message text (if available)
2. Fall back to session language (if exists)
3. Fall back to Telegram locale (if available)
4. Default to English

### AI Prompt Structure (for development reference)
```
System Prompt:
"You are an expert Tarot card reader. Provide interpretations based on traditional Tarot meanings while connecting cards to the user's specific question. Be insightful, supportive, and culturally appropriate. Keep interpretations under 4000 characters."

User Prompt (Automated Reading):
"Question: {user_question}
Cards drawn: {card_1_name} (Past), {card_2_name} (Present), {card_3_name} (Future)
Card meanings: {card_1_meaning}, {card_2_meaning}, {card_3_meaning}

Provide a 3-card reading interpretation in {language}."

User Prompt (Custom Interpretation):
"Cards: {card_1_name}, {card_2_name}, {card_3_name}
Card meanings: {card_1_meaning}, {card_2_meaning}, {card_3_meaning}

Provide an interpretation of this card combination in {language}."
```

---

## Contract Version
**Version**: 1.0
**Last Updated**: 2025-12-04
**Status**: Ready for implementation

**Next Steps**: Use this contract for Test-Driven Development (write contract tests before implementation).
