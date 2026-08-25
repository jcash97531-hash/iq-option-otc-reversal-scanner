# iq-option-otc-reversal-scanner

Real-time OTC reversal scanner for IQ Option with Telegram alerts - detects 6 consecutive candles in one direction and sends instant notifications.

## Features

- ✅ Real-time candle monitoring across multiple currency pairs
- ✅ Detects 6 consecutive candles moving in the same direction (UP or DOWN)
- ✅ Instant Telegram alerts when patterns are found
- ✅ Efficient IQ Option API integration
- ✅ Automatic reconnection handling
- ✅ Comprehensive logging
- ✅ Memory-efficient candle buffering

## Requirements

- Python 3.8+
- IQ Option account
- Telegram bot token and chat ID

## Installation

1. Clone the repository:
```bash
git clone https://github.com/jcash97531-hash/iq-option-otc-reversal-scanner.git
cd iq-option-otc-reversal-scanner
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file from template:
```bash
cp .env.example .env
```

4. Configure your credentials in `.env`:
```
IQ_OPTION_EMAIL=your_email@example.com
IQ_OPTION_PASSWORD=your_password
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
ASSETS=EURUSD,GBPUSD,USDJPY
TIMEFRAME=1
CHECK_INTERVAL=10
REVERSAL_LENGTH=6
```

## Configuration

### Environment Variables

- **IQ_OPTION_EMAIL** - Your IQ Option account email
- **IQ_OPTION_PASSWORD** - Your IQ Option account password
- **TELEGRAM_BOT_TOKEN** - Telegram bot token (get from @BotFather)
- **TELEGRAM_CHAT_ID** - Your Telegram chat ID
- **ASSETS** - Comma-separated list of assets to monitor (e.g., `EURUSD,GBPUSD`)
- **TIMEFRAME** - Candle timeframe in minutes (1, 5, 15, 30, 60)
- **CHECK_INTERVAL** - Seconds between candle checks
- **REVERSAL_LENGTH** - Number of consecutive candles (default: 6)

### Getting Telegram Credentials

1. Create a bot with @BotFather on Telegram
2. Get your chat ID by messaging @userinfobot
3. Add the bot token and chat ID to `.env`

## Usage

Run the scanner:
```bash
python scanner.py
```

The scanner will:
1. Connect to IQ Option
2. Load initial candle data for all configured assets
3. Begin monitoring in real-time
4. Send Telegram alerts when patterns are detected
5. Log all activity to `scanner.log`

## Architecture

```
scanner.py          Main orchestrator and scan loop
├── iq_client.py    IQ Option API wrapper
├── reversal_detector.py  Pattern detection logic
└── telegram_alerts.py    Telegram notification sender

config.py           Configuration loader
```

### How It Works

1. **Connection**: Connects to IQ Option WebSocket API
2. **Initialization**: Loads recent candles for all monitored assets
3. **Monitoring Loop**: Checks each asset every `CHECK_INTERVAL` seconds
4. **Pattern Detection**: Checks if last 6 candles are all UP or all DOWN
5. **Alerting**: Sends Telegram message when pattern is found
6. **Deduplication**: Prevents duplicate alerts for same pattern

### Pattern Detection

A reversal is detected when 6 consecutive candles move in the same direction:

- **UP**: `close > open` for all 6 candles
- **DOWN**: `close < open` for all 6 candles

Once detected, alerts are sent once per direction change per asset.

## Logs

Logs are written to both console and `scanner.log`:

```
2026-08-25 10:30:45 - scanner - INFO - Initializing OTC Reversal Scanner...
2026-08-25 10:30:46 - scanner - INFO - Connected to IQ Option
2026-08-25 10:30:47 - scanner - INFO - Loaded 11 candles for EURUSD
...
2026-08-25 10:35:12 - scanner - INFO - 🚨 Reversal detected: EURUSD UP (6 candles) @ 1.08542
```

## Troubleshooting

### Connection Failed
- Verify IQ Option email and password
- Check internet connection
- Ensure IQ Option account is active

### No Alerts
- Check Telegram bot token and chat ID
- Verify ASSETS list matches IQ Option asset names
- Review `scanner.log` for errors
- Try lower timeframes (1 or 5 minutes)

### High CPU Usage
- Increase `CHECK_INTERVAL` (delay between checks)
- Reduce number of monitored ASSETS
- Use larger timeframes

## Performance

- **Memory**: ~1-2 MB per asset (keeps 20 candles per asset)
- **CPU**: Minimal, depends on CHECK_INTERVAL
- **Network**: Low bandwidth, efficient API usage
- **Latency**: <1 second from pattern detection to Telegram alert

## License

MIT

## Disclaimer

This scanner is for educational purposes. Cryptocurrency and forex trading carry risk. Always validate signals before trading and use proper risk management.
