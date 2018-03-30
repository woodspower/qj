{
    "InferenceName": "Movie",
    "Sequence": [
        {
            "Name": "One of Confirm->dNext->Cancel->Reject",
            "KeyBody": [
                {
                    "Name": "Any kind of Confirm",
                    "Conditions": [
                        {
                            "Name": "",
                            "Allow": [
                                {
                                    "Name": "",
                                    "Percent": 1.0,
                                    "Tags": ["Confirm"]
                                }
                            ],
                            "Disallow": []
                        }
                    ],
                    "Actions": [
                        {
                            "Name": "Click center",
                            "Command": "Click",
                            "DecisionPeriod": 99,
                            "StartTag": ["Confirm"],
                            "StartOffset": [0.5, 0.5],
                            "EndTag": [],
                            "EndOffset": [],
                            "Duration": "2~5"
                        }
                    ]
                },
                {
                    "Name": "Dialog Next",
                    "Conditions": [
                        {
                            "Name": "",
                            "Allow": [
                                {
                                    "Name": "",
                                    "Percent": 1.0,
                                    "Tags": ["dNext"]
                                }
                            ],
                            "Disallow": []
                        }
                    ],
                    "Actions": [
                        {
                            "Name": "Click center",
                            "Command": "Click",
                            "DecisionPeriod": 99,
                            "StartTag": ["dNext"],
                            "StartOffset": [0.5, 0.5],
                            "EndTag": [],
                            "EndOffset": [],
                            "Duration": "2~5"
                        }
                    ]
                },
                {
                    "Name": "If Cancel",
                    "Conditions": [
                        {
                            "Name": "",
                            "Allow": [
                                {
                                    "Name": "",
                                    "Percent": 1.0,
                                    "Tags": ["Cancel"]
                                }
                            ],
                            "Disallow": []
                        }
                    ],
                    "Actions": [
                        {
                            "Name": "Click center",
                            "Command": "Click",
                            "DecisionPeriod": 99,
                            "StartTag": ["Cancel"],
                            "StartOffset": [0.5, 0.5],
                            "EndTag": [],
                            "EndOffset": [],
                            "Duration": "2~5"
                        }
                    ]
                },
                {
                    "Name": "Reject if nothing",
                    "Conditions": [
                        {
                            "Name": "",
                            "Allow": [
                                {
                                    "Name": "",
                                    "Percent": 1.0,
                                    "Tags": ["Reject"]
                                }
                            ],
                            "Disallow": []
                        }
                    ],
                    "Actions": [
                        {
                            "Name": "Click center",
                            "Command": "Click",
                            "DecisionPeriod": 99,
                            "StartTag": ["Reject"],
                            "StartOffset": [0.5, 0.5],
                            "EndTag": [],
                            "EndOffset": [],
                            "Duration": "2~5"
                        }
                    ]
                }
            ]
        }
    ]
}
