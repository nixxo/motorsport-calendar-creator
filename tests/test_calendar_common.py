from motorsport_calendar_creator import calendar_common as cc


def test_str_enc():
    assert list(cc.str_enc("ciao")) == ["ciao\n"]
    assert list(cc.str_enc("ciao\r\nprova")) == ["ciao\n", "prova\n"]


def test_enc_str():
    # 'AutÃ³dromo Internacional do Algarve - PortimÃ£o'
    # 'Autódromo Internacional do Algarve - Portimão'
    assert cc.enc_str("à") == "Ã\xa0"


def test_check_url():
    test_data = [
        {
            "input": ["https://www.test.com/ciao", "https://www.test.com"],
            "output": "https://www.test.com/ciao",
        },
        {
            "input": ["ciao", "https://www.test.com"],
            "output": "https://www.test.com/ciao",
        },
        {
            "input": ["/ciao", "https://www.test.com/"],
            "output": "https://www.test.com/ciao",
        },
    ]
    for data in test_data:
        assert cc.check_url(data["input"][0], data["input"][1]) == data["output"]
