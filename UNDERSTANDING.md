The project is basically about controlling how much people can use a paid AI service.

We have users with API keys, and each user has a certain limit for how many requests they can make and how many tokens they can use. The program gets a list of requests from a file and checks them one by one.

For each request, it checks if the request is valid, if the API key is known, and if the user is still within their limits. If everything is fine, the request is allowed. If not, it gets rejected and the program records the reason and how long the user has to wait before trying again.

One thing that makes this project a little different is that even a request that gets rejected can still count toward the request limit, but it doesn't use any tokens. Also, the limits are based on the actual calendar minute and hour, instead of looking at the previous amount of time.

So basically, we are making a system that looks at each AI request and decides whether to let it through or reject it based on the user's limits


Project overview
You are given a file containing API requests and their timestamps, along with a list of API keys and their usage limits. Each user can make a certain number of requests and use a certain number of tokens per minute and hour. Your task is to build a system that processes these requests and determines whether they should be allowed or rejected based on the usage limits.

Request processing
The system processes requests in the order they appear in the input file. For each request, it performs the following checks:
1. Validate the request: Check if the request format is valid. A valid request should have a non-empty API key and a valid timestamp.
2. Check API key: Verify if the provided API key exists in the system.
3. Check rate limits:
	•	For each API key, there are two rate limits: requests per minute and tokens per minute. Additionally, there is a request limit per hour.
	•	The system calculates the number of requests made by each API key within the current minute and hour.
	•	The token usage is also tracked per minute.

Handling rejected requests
•	Even if a request is rejected, it still counts towards the request limit for the current minute and hour.
•	However, rejected requests do not consume any tokens.
•	When a request is rejected, the system records the reason and calculates the time until the user can make another request (backoff time).

Calculating backoff time
The backoff time is calculated based on the type of limit that was exceeded:
•	Requests per minute limit: The backoff time is the number of seconds remaining in the current minute.
•	Tokens per minute limit: The backoff time is the number of seconds remaining in the current minute.
•	Requests per hour limit: The backoff time is the number of seconds remaining in the current hour.

Output
The system should output the result for each request, indicating whether it was allowed or rejected, along with the reason and backoff time if applicable.

Additional requirements
•	The system should use Python for implementation.
•	The program should be able to process multiple requests from the input file.
•	The solution should be efficient and handle large inputs effectively.

Constraints
•	API keys are always 64-character alphanumeric strings.
•	Timestamps are in seconds since the epoch.
•	A request is considered "per minute" from the start of the current calendar minute (e.g., from :00 to :59) and "per hour" from the start of the current hour (e.g., from :00:00 to :59:59).
•	A user cannot make more requests than their limit, even if some of those requests are rejected.