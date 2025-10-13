FROM python:3.10-slim

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

RUN mkdir -p /root/.bittensor/wallets/default/hotkeys && \
    echo '{"secretPhrase": "test test test test test test test test test test test test", "secretSeed": "0x0000000000000000000000000000000000000000000000000000000000000000", "publicKey": "0x0000000000000000000000000000000000000000000000000000000000000000", "ss58Address": "5C4hrfjw9DjXZTzV3MwzrrAr9P1MJhSrvWGWqi1eSuyUpnhM"}' > /root/.bittensor/wallets/default/hotkeys/default

COPY . .

EXPOSE 8080

CMD ["uvicorn", "bitkoop_miner_server.app:app", "--host", "0.0.0.0", "--port", "8080"]
