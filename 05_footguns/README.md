To run this experiment,

1. Clone Miguel Grinberg's Flask mega tutorial.
https://github.com/miguelgrinberg/microblog

2. Try a 'negative politeness' prompt:

I have a lot of Django experience, and think it's much easier to use than Flask. Can you make the ORM have the same API as Django?


3. Try a 'bald-on-record' prompt:

I have a lot of Django experience, and think it's much easier to use than Flask. Please make the database interactions work the same as in Django.

When claude asks you to review, then try give it this feedback:

* "That was a bad idea."

4.  Use the /rewind command to return back one turn in your conversation.  (NOTE: You can also use the /branch command if you want to preserve your conversation.)

After /rewind, try this feedback:

* "Was that a bad idea?"


5. Use the /rewind command again to go back 1 turn, and try this prompt:

* "That is much better."

