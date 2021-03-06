# flexworkers-bot

**_Python 3.x required._**

## USAGE

- Install required libraries: `pip3 install -r requirements.txt`.
- Obtain your [Telegram API ID](https://core.telegram.org/api/obtaining_api_id).
- Create a Telegram bot with [@BotFather](https://t.me/botfather).
- Set your API ID, API Hash and the token provided by BotFather in the config file.
- Set your [Telegram Chat ID](https://t.me/getmyid_bot), Flexpool ETH address and preferred currency in the config file.
- Start bot: `python3 bot.py`.

The bot begins to collect data from the day it's run for the first time, it's impossible to obtain the earnings of each worker from previous days.

The script **must be running all the time** to collect daily data from the Flexpool API and for the bot to receive the commands.

You'll receive your earnings for the day at 00:05. You can also check all your collected earnings in the `earnings` folder.

In the event that one day's data has not been collected, you can manually run `python3 earnings.py`, otherwise the earnings will be accumulated along with those of the following day but won't be accurate for each worker.

## Available Commands

- **/help**  - See all available commands.
- **/day** _yesterday_ | _YYYY-mm-dd_ - Get earnings.
- **/summary** _start_ | _end_ - Get summary.
- **/price** _currency_ - Get current ETH price.
- **/currency** _symbol_ - Change your currency.
- **/workers** - List workers.

## Summaries Examples

![Earnings per Day](examples/bars.jpg)

![Accumulated Earnings](examples/lines.jpg)
