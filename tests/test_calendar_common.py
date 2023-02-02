from motorsport_calendar_creator.calendar_common import CalendarCommon

cc = CalendarCommon()


def test_calendar_common_methods():
    test_data = {
        cc.str_enc: [
            {
                "input": ["ciao"],
                "output": ["ciao\n"],
            },
            {
                "input": ["ciao\r\nprova"],
                "output": ["ciao\n", "prova\n"],
            },
        ],
        cc.enc_str: [
            {
                "input": ["Autódromo Internacional do Algarve - Portimão"],
                "output": "AutÃ³dromo Internacional do Algarve - PortimÃ£o",
            },
        ],
        cc.check_url: [
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
        ],
    }

    for method in test_data:
        for data in test_data[method]:
            assert method(*data["input"]) == data["output"]
