from fizzbuzz.output import output_stdout, build_payload

# didn't write tests for output_speak or output_webhook actually doing
# their thing - speak needs your speakers/audio setup and webhook needs
# a real url to hit, and I don't really know how to fake either of those
# in a test. I just ran them manually from the CLI (--output speak and
# --output webhook against a test webhook.site url) and confirmed they
# worked that way. build_payload() is the one part of the webhook code
# that's just plain logic, so that's the part I actually test here.


def test_output_stdout_prints_each_line(capsys):
    output_stdout(["1", "2", "Fizz"])
    captured = capsys.readouterr()
    assert captured.out == "1\n2\nFizz\n"


def test_build_payload():
    assert build_payload(["1", "Fizz", "Buzz"]) == {
        "results": ["1", "Fizz", "Buzz"]
    }
