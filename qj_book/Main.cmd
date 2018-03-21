{
    "InferenceName": "Main",
    "InferenceFile": "/home/leo/qj/object_detection/data/Main/inference_ssd/frozen_inference_graph.pb",
    "LabelMapFile": "/home/leo/qj/object_detection/data/Main/pascal_label_map.pbtxt",
    "Sequence": [
        {
            "Name": "Do Task, choose one of the following",
            "KeyBody": [
                {
                    "Name": "ZhuXian Task",
                    "Conditions": {
                            "Name": "",
                            "Allow":{
                                    "Name": "",
                                    "Percent": 1.0,
                                    "Tags": [
                                        "tZhuXian"
                                    ]
                            },
                            "Disallow": [
                                {
                                    "Name": "cancel when task not ready",
                                    "Seconds": 0,
                                    "Tags": [
                                        "tTaskNotReady"
                                    ]
                                },
                                {
                                    "Name": "cancel when fightoff for 60secs",
                                    "Seconds": 60,
                                    "Tags": [
                                        "FightOff"
                                    ]
                                }
                            ]
                    },
                    "Actions": [
                        {
                            "Name": "Click center",
                            "Command": "Click",
                            "DecisionPeriod": 5000,
                            "StartTag": [
                                "tZhuXian"
                            ],
                            "StartOffset": [
                                0.5,
                                0.5
                            ],
                            "EndTag": [],
                            "EndOffset": [],
                            "Duration": "2~5"
                        }
                    ]
                },
                {
                    "Name": "RiChang Task",
                    "Conditions": [
                        {
                            "Name": "",
                            "Allow": [
                                {
                                    "Name": "",
                                    "Percent": 1.0,
                                    "Tags": [
                                        "tRiChang"
                                    ]
                                }
                            ],
                            "Disallow": []
                        }
                    ],
                    "Actions": [
                        {
                            "Name": "Click center",
                            "Command": "Click",
                            "DecisionPeriod": 5000,
                            "StartTag": [
                                "tRiChang"
                            ],
                            "StartOffset": [
                                0.5,
                                0.5
                            ],
                            "EndTag": [],
                            "EndOffset": [],
                            "Duration": "2~5"
                        }
                    ]
                }
            ]
        },
        {
            "Name": "Start fight in case not auto started in Copier mode",
            "KeyBody": [
                {
                    "Name": "If there is LeaveBox, and FightOff for 60seconds",
                    "Conditions": [
                        {
                            "Name": "",
                            "Allow": [
                                {
                                    "Name": "",
                                    "Percent": 1.0,
                                    "Seconds": 60,
                                    "Tags": [
                                        "FightOff",
                                        "LeaveBox"
                                    ]
                                }
                            ],
                            "Disallow": []
                        }
                    ],
                    "Actions": [
                        {
                            "Name": "Trun on Fight",
                            "Command": "Click",
                            "DecisionPeriod": 5000,
                            "StartTag": [
                                "FightOff"
                            ],
                            "StartOffset": [],
                            "EndTag": [],
                            "EndOffset": [],
                            "Duration": "2~5"
                        }
                    ]
                }
            ]
        },
        {
            "Name": "Follow Guider in Copier mode, to finish tasks",
            "KeyBody": [
                {
                    "Name": "gLeftArrow",
                    "Conditions": [
                        {
                            "Name": "",
                            "Allow": [
                                {
                                    "Name": "",
                                    "Percent": 1.0,
                                    "Tags": [
                                        "gLeftArrow",
                                        "LeaveBox"
                                    ]
                                }
                            ],
                            "Disallow": []
                        }
                    ],
                    "Actions": [
                        {
                            "Name": "P(-1/2w,1/2h)",
                            "Command": "Click",
                            "DecisionPeriod": 499,
                            "StartTag": [
                                "gLeftArrow"
                            ],
                            "StartOffset": [
                                -0.5,
                                0.5
                            ],
                            "EndTag": [],
                            "EndOffset": [],
                            "Duration": "2~5"
                        }
                    ]
                },
                {
                    "Name": "gRightArrow",
                    "Conditions": [
                        {
                            "Name": "",
                            "Allow": [
                                {
                                    "Name": "",
                                    "Percent": 1.0,
                                    "Tags": [
                                        "gRightArrow",
                                        "LeaveBox"
                                    ]
                                }
                            ],
                            "Disallow": []
                        }
                    ],
                    "Actions": [
                        {
                            "Name": "P(3/2w,1/2h)",
                            "Command": "Click",
                            "DecisionPeriod": 499,
                            "StartTag": [
                                "gRightArrow"
                            ],
                            "StartOffset": [
                                1.5,
                                0.5
                            ],
                            "EndTag": [],
                            "EndOffset": [],
                            "Duration": "2~5"
                        }
                    ]
                },
                {
                    "Name": "gUpArrow",
                    "Conditions": [
                        {
                            "Name": "",
                            "Allow": [
                                {
                                    "Name": "gUpArrow",
                                    "Percent": 1.0,
                                    "Tags": [
                                        "gUpArrow",
                                        "LeaveBox"
                                    ]
                                }
                            ],
                            "Disallow": []
                        }
                    ],
                    "Actions": [
                        {
                            "Name": "P(1/2w,-1/2h)",
                            "Command": "Click",
                            "DecisionPeriod": 499,
                            "StartTag": [
                                "gUpArrow"
                            ],
                            "StartOffset": [
                                0.5,
                                -0.5
                            ],
                            "EndTag": [],
                            "EndOffset": [],
                            "Duration": "2~5"
                        }
                    ]
                },
                {
                    "Name": "gDownArrow",
                    "Conditions": [
                        {
                            "Name": "",
                            "Allow": [
                                {
                                    "Name": "gDownArrow",
                                    "Percent": 1.0,
                                    "Tags": [
                                        "gDownArrow",
                                        "LeaveBox"
                                    ]
                                }
                            ],
                            "Disallow": []
                        }
                    ],
                    "Actions": [
                        {
                            "Name": "P(1/2w,3/2h)",
                            "Command": "Click",
                            "DecisionPeriod": 499,
                            "StartTag": [
                                "gDownArrow"
                            ],
                            "StartOffset": [
                                0.5,
                                1.5
                            ],
                            "EndTag": [],
                            "EndOffset": [],
                            "Duration": "2~5"
                        }
                    ]
                },
                {
                    "Name": "gLeftUpArrow",
                    "Conditions": [
                        {
                            "Name": "",
                            "Allow": [
                                {
                                    "Name": "gLeftUpArrow",
                                    "Percent": 1.0,
                                    "Tags": [
                                        "gLeftUpArrow",
                                        "LeaveBox"
                                    ]
                                }
                            ],
                            "Disallow": []
                        }
                    ],
                    "Actions": [
                        {
                            "Name": "P(-1/2w,-1/2h)",
                            "Command": "Click",
                            "DecisionPeriod": 499,
                            "StartTag": [
                                "gLeftUpArrow"
                            ],
                            "StartOffset": [
                                -0.5,
                                -0.5
                            ],
                            "EndTag": [],
                            "EndOffset": [],
                            "Duration": "2~5"
                        }
                    ]
                },
                {
                    "Name": "gRightUpArrow",
                    "Conditions": [
                        {
                            "Name": "",
                            "Allow": [
                                {
                                    "Name": "gRightUpArrow",
                                    "Percent": 1.0,
                                    "Tags": [
                                        "gRightUpArrow",
                                        "LeaveBox"
                                    ]
                                }
                            ],
                            "Disallow": []
                        }
                    ],
                    "Actions": [
                        {
                            "Name": "P(1.5, -0.5)",
                            "Command": "Click",
                            "DecisionPeriod": 499,
                            "StartTag": [
                                "gRightUpArrow"
                            ],
                            "StartOffset": [
                                1.5,
                                -0.5
                            ],
                            "EndTag": [],
                            "EndOffset": [],
                            "Duration": "2~5"
                        }
                    ]
                },
                {
                    "Name": "gLeftDownArrow",
                    "Conditions": [
                        {
                            "Name": "",
                            "Allow": [
                                {
                                    "Name": "gLeftDownArrow",
                                    "Percent": 1.0,
                                    "Tags": [
                                        "gLeftDownArrow",
                                        "LeaveBox"
                                    ]
                                }
                            ],
                            "Disallow": []
                        }
                    ],
                    "Actions": [
                        {
                            "Name": "P(-0.5, 1.5)",
                            "Command": "Click",
                            "DecisionPeriod": 499,
                            "StartTag": [
                                "gLeftDownArrow"
                            ],
                            "StartOffset": [
                                -0.5,
                                1.5
                            ],
                            "EndTag": [],
                            "EndOffset": [],
                            "Duration": "2~5"
                        }
                    ]
                },
                {
                    "Name": "gRightDownArrow",
                    "Conditions": [
                        {
                            "Name": "",
                            "Allow": [
                                {
                                    "Name": "gRightDownArrow",
                                    "Percent": 1.0,
                                    "Tags": [
                                        "gRightDownArrow",
                                        "LeaveBox"
                                    ]
                                }
                            ],
                            "Disallow": []
                        }
                    ],
                    "Actions": [
                        {
                            "Name": "P(1.5, 1.5)",
                            "Command": "Click",
                            "DecisionPeriod": 499,
                            "StartTag": [
                                "gRightDownArrow"
                            ],
                            "StartOffset": [
                                1.5,
                                1.5
                            ],
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
