# different ways to "output" the fizzbuzz results.
# I split build_payload() out from output_webhook() so I could actually
# write a test for the webhook stuff without needing a real server to
# send the request to (I don't really know how to fake/mock a network
# call, so this was my workaround - just test the part that builds the
# data, and test the actual sending part by hand)


def output_stdout(lines: list[str]) -> None:
    """Just prints everything, one per line. The default, easy one."""
    for line in lines:
        print(line)


def output_speak(lines: list[str]) -> None:
    """Reads the results out loud using pyttsx3.

    pyttsx3 works offline and is supposedly cross platform (uses different
    speech engines under the hood depending on your OS - on Mac it uses
    the built in NSSpeechSynthesizer stuff, on Linux it needs espeak
    installed). I only actually tested this on my Mac, so if you're on
    Linux and it doesn't say anything, you probably need to
    `sudo apt install espeak` first.
    """
    import pyttsx3

    engine = pyttsx3.init()
    for line in lines:
        engine.say(line)
    engine.runAndWait()


def build_payload(lines: list[str]) -> dict:
    """Builds the JSON body we send to the webhook.

    Pulled this into its own function mainly so I could unit test it
    without actually making a network call.
    """
    return {"results": lines}


def output_webhook(lines: list[str], url: str) -> None:
    """POSTs the results to some webhook url as JSON.

    Didn't do anything fancy with retries or timeouts settings really,
    just a plain requests.post. If the url is bad or the server errors
    out this will raise an exception and the script will just crash,
    which is probably fine for what this is.
    """
    import requests

    payload = build_payload(lines)
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    return response
