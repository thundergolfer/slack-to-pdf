from click.testing import CliRunner

from slackviewer import main

def test_main():
    runner = CliRunner()
    result = runner.invoke(main, [5000, 'test.zip','localhost'])

if __name__ == '__main__':
    test_main()