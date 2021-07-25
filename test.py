import praw

reddit = praw.Reddit(
    client_id="HBtFanSntocxgSWJT8KnXA",
    client_secret="rYWaEamC6Y8fZ96WUvuzB0peSZ3CuA",
    user_agent="discord:angry-cat:1.0",
)

title = "Not found"
url = ""
for submission in reddit.subreddit("aww").new(limit=None):
    if submission.url.endswith(('.jpg', '.png', '.gif', '.jpeg')):
        url = submission.url
        title = submission.title
        print(url)
        print(title)
        break