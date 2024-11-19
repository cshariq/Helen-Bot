# Helen-Bot
Helen bot is a multipurpose discord bot. It has several features such as:
- A mathcmaking command that provides a % match between users based on the statistics of the server
- 'I'm' and 'You're' detection. Responds back as Hi ---, I'm Helen when bot detect 'I'm' and responds back as 'No they are [user name]' when'You're is detected'. Also supports accronyms for the key words, for example 'u r' would be detected as 'You're'.
- Adds moai reaction on every message in a specified channel. *As of right now only my server is supported as thats the referencec link, if you'd like moai reactions in a server of you're own you can change the link to you're respective server.*
- Adds gemini support, so when you're group is wondering something you can search something up quickly using the bot's gemini command(by default, uses gemini flash model for quick responses, could be change by configuring the command on use). Gemini also understands the context of what users are talking about if used in a chain of replies.
- Randomely responds to users using context and gemini, this adds a bit of fun to your discord server!
- Radomely or upon mention of some words, responds with a keyword, also add fun to your discord server!

This bot uses complex data collection method to provide its services. For example to provide accurate matchmaking results, upon the addition of the bot to a new server it will scan all message and weight each intercation uniquely. Based the type interaction between 2 users, the pair will be given points. The more direct the interaction the more points. *If you have an amazing match with a person, your score can go above 100%!!*

We have also well integrated gemini by defaulting it to short simple responses. Although this does limit its creativity, I think most people when using this bot would be looking for a short and sweet response. If not, they can configure their preferred settings by running the gemini command everytime they want to ask something. 

Moreover, all UI's provided by the bot are high quality and use high quality images/icons(except when providing matchmaking results, the bot takes the profile pictures of users to display them with may or may not be high quality). Our bot also has french integrated into it to give it some humour!

Want new features? Provide some feedback!! I'll also am regularly looking at issues and pull request to continuely improve this project.

Example usage of gemini:
<img width="1536" alt="image" src="https://github.com/user-attachments/assets/e900ff21-60d6-4132-95f7-d66adfba1aa8">
