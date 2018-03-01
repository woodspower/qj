{
    "Index": [
        {
            "Name": "If StartGame GUI",
            "KeyBody": [
                {
                    "Name": "",
                    "Conditions": [
                        {
                            "Name": "",
                            "Allow": [
                                {
                                    "Name": "",
                                    "Percent": 1.0,
                                    "Tags": ["StartGame"]
                                }
                            ],
                            "Disallow": []
                        }
                    ],
                    "Actions": [
                        {
                            "Name": "",
                            "Command": "Goto",
                            "DecisionPeriod": 0,
                            "BookName": "StartGame"
                        }
                    ]
                }
            ]
        },
        {
            "Name": "If Movie GUI",
            "KeyBody": [
                {
                    "Name": "",
                    "Conditions": [
                        {
                            "Name": "",
                            "Allow": [
                                {
                                    "Name": "",
                                    "Percent": 1.0,
                                    "Tags": ["Movie"]
                                }
                            ],
                            "Disallow": []
                        }
                    ],
                    "Actions": [
                        {
                            "Name": "Click center",
                            "Command": "Click",
                            "DecisionPeriod": 1000,
                            "StartTag": ["Movie"],
                            "StartOffset": [0.889, 0.921],
                            "EndTag": [],
                            "EndOffset": [],
                            "Duration": "2~5"
                        },
                        {
                            "Name": "Then Goto...",
                            "Command": "Goto",
                            "DecisionPeriod": 0,
                            "BookName": "Movie"
                        }
                    ]
                }
            ]
        },
        {
            "Name": "If Main GUI",
            "KeyBody": [
                {
                    "Name": "",
                    "Conditions": [
                        {
                            "Name": "",
                            "Allow": [
                                {
                                    "Name": "",
                                    "Percent": 1.0,
                                    "Tags": ["Main"]
                                }
                            ],
                            "Disallow": []
                        }
                    ],
                    "Actions": [
                        {
                            "Name": "Click TaskBar",
                            "Command": "Click",
                            "DecisionPeriod": 5000,
                            "StartTag": ["Main"],
                            "StartOffset": [0.1076, 0.2715],
                            "EndTag": [],
                            "EndOffset": [],
                            "Duration": "2~5"
                        },
                        {
                            "Name": "Then Goto...",
                            "Command": "Goto",
                            "DecisionPeriod": 0,
                            "BookName": "Main"
                        }
                    ]
                }
            ]
        }
    ]
}
