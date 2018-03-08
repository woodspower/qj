{
    "Name": "Main",
    "InferenceFile": "/home/leo/qj/object_detection/data/Main/inference_ssd/frozen_inference_graph.pb",
    "LabelMapFile": "/home/leo/qj/object_detection/data/Main/pascal_label_map.pbtxt",
    "Sequence": [
        {
            "Name": "Follow Guider",
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
                                        "Guider",
                                        "gLeftArrow"
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
                            "DecisionPeriod": 99,
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
                                        "Guider",
                                        "gRightArrow"
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
                            "DecisionPeriod": 99,
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
                                        "Guider",
                                        "gUpArrow"
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
                            "DecisionPeriod": 99,
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
                                        "Guider",
                                        "gDownArrow"
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
                            "DecisionPeriod": 99,
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
                                        "Guider",
                                        "gLeftUpArrow"
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
                            "DecisionPeriod": 99,
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
                                        "Guider",
                                        "gRightUpArrow"
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
                            "DecisionPeriod": 99,
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
                                        "Guider",
                                        "gLeftDownArrow"
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
                            "DecisionPeriod": 99,
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
                                        "Guider",
                                        "gRightDownArrow"
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
                            "DecisionPeriod": 99,
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
        },
        {
            "Name": "Do Task",
            "KeyBody": [
                {
                    "Name": "ZhuXian Task",
                    "Conditions": [
                        {
                            "Name": "",
                            "Allow": [
                                {
                                    "Name": "",
                                    "Percent": 1.0,
                                    "Tags": [
                                        "tZhuXian"
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
                            "DecisionPeriod": 99,
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
                }
            ]
        }
    ]
}
