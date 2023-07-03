# wyyxxyctf
我永远喜欢永雏塔菲

## Prompts
Act as an experienced python engineer, write a script to do the following tasks:
1. We will first load necessary urls from the .env file as below:
   ```python
    from dotenv import load_dotenv
    import os

    # Load the .env file
    load_dotenv()

    # Now you can access the variables as environment variables
    weibo_url = os.getenv('WEIBO_URL')
    message_webhook_url = os.getenv('MESSAGE_WEBHOOK_URL')
    status_webhook_url = os.getenv('STATUS_WEBHOOK_URL')
    ```
2. For every X minutes, parse the content of the weibo_url, and send any new weibo posts to message_webhook_url. Notice that we can have both text and image posts, embed them using discord's embed feature.
3. For every 1 hour, send a signal to status_webhook_url to indicate that the script is still running.
4. The script should be able to run on both MacOS and Linux and Windows.
5. Use pm2 to manage the script, and make sure it can restart automatically when it crashes.