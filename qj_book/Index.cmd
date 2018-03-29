{
    "InferenceName": "Index",
    "InferenceFile":"/home/leo/qj/object_detection/data/Index/inference_ssd/frozen_inference_graph.pb",
    "LabelMapFile":"/home/leo/qj/object_detection/data/Index/pascal_label_map.pbtxt",
    "Sequence": [
        {
            "Name": "Go to one of following GUI",
            "KeyBody": [
                {
                    "Name": "If StartGame GUI",
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
                },
                {
                    "Name": "If Movie GUI",
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
                            "Name": "Click bottom at first",
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
                },
                {
                    "Name": "If Main GUI",
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
                            "Name": "Then Goto...",
                            "Command": "Goto",
                            "DecisionPeriod": 0,
                            "BookName": "Main"
                        }
                    ]
                },
                {
                    "Name": "If Copier GUI",
                    "Conditions": {
                            "Allow": { "Tags": "CopierMenu"}
                        },
                    "Actions": {
                            "Command": "Goto",
                            "BookName": "CopierSubmenu"
                        }
                },
                {
                    "Name": "If any other fight GUI",
                    "Conditions": [
                        {
                            "Name": "",
                            "Allow": [
                                {
                                    "Name": "",
                                    "Percent": 0.01,
                                    "Tags": ["EnforceMenu", "ActorMenu", "WingMenu"]
                                }
                            ],
                            "Disallow": []
                        }
                    ],
                    "Actions": [
                        {
                            "Name": "Use Main temporary",
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
