# TrainDeathToll

Visualize CD problems from Twitter @cdmimoradnosti


## Run it locally

- Install Google AppEngine Python SDK
- create `env.json` file with your Twitter API credentials as follows:

```{.json}
{
	"CONSUMER_KEY": "<TWITTER CONSUMER KEY>",
	"CONSUMER_SECRET": "<TWITTER CONSUMER SECRET>",
	"ACCESS_KEY": "<TWITTER ACCESS TOKEN>",
	"ACCESS_SECRET": "<TWITTER ACCESS KEY>"
}
```

- Run using development server:

```{.sh}
$ dev_appserver.py .
```

By default, the app will be at `http://localhost:8080`, administration panel at `http://localhost:8000`
