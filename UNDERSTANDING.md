The project is basically about controlling how much people can use a paid AI service.

We have users with API keys, and each user has a certain limit for how many requests they can make and how many tokens they can use. The program gets a list of requests from a file and checks them one by one.

For each request, it checks if the request is valid, if the API key is known, and if the user is still within their limits. If everything is fine, the request is allowed. If not, it gets rejected and the program records the reason and how long the user has to wait before trying again.

One thing that makes this project a little different is that even a request that gets rejected can still count toward the request limit, but it doesn't use any tokens. Also, the limits are based on the actual calendar minute and hour, instead of looking at the previous amount of time.

So basically, we are making a system that looks at each AI request and decides whether to let it through or reject it based on the user's limits