{
    "Name": "Main",
    "InferenceFile":"/home/leo/qj/object_detection/data/Main/inference_frcnn/frozen_inference_graph.pb",
    "LabelMapFile":"/home/leo/qj/object_detection/data/Main/pascal_label_map.pbtxt",
    "Sequence": [
        {
            "Name": "Follow Guider",
            "KeyBody": [
                {
                    "Name": "LeftArrow",
                    "Conditions": [
                        {
                            "Name": "",
                            "Allow": [
                                {
                                    "Name": "",
                                    "Percent": 1.0,
                                    "Tags": [
                                        "Guider",
                                        "LeftArrow"
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
                            "DecisionPeriod": 1000,
                            "StartTag": [
                                "LeftArrow"
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
                    "Name": "RightArrow",
                    "Conditions": [
                        {
                            "Name": "",
                            "Allow": [
                                {
                                    "Name": "",
                                    "Percent": 1.0,
                                    "Tags": [
                                        "Guider",
                                        "RightArrow"
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
                            "DecisionPeriod": 1000,
                            "StartTag": [
                                "RightArrow"
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
                    "Name": "UpArrow",
                    "Conditions": [
                        {
                            "Name": "",
                            "Allow": [
                                {
                                    "Name": "UpArrow",
                                    "Percent": 1.0,
                                    "Tags": [
                                        "Guider",
                                        "UpArrow"
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
                            "DecisionPeriod": 1000,
                            "StartTag": [
                                "UpArrow"
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
                    "Name": "DownArrow",
                    "Conditions": [
                        {
                            "Name": "",
                            "Allow": [
                                {
                                    "Name": "DownArrow",
                                    "Percent": 1.0,
                                    "Tags": [
                                        "Guider",
                                        "DownArrow"
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
                            "DecisionPeriod": 1000,
                            "StartTag": [
                                "DownArrow"
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
                    "Name": "LeftUpArrow",
                    "Conditions": [
                        {
                            "Name": "",
                            "Allow": [
                                {
                                    "Name": "LeftUpArrow",
                                    "Percent": 1.0,
                                    "Tags": [
                                        "Guider",
                                        "LeftUpArrow"
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
                            "DecisionPeriod": 1000,
                            "StartTag": [
                                "LeftUpArrow"
                            ],
                            "StartOffset": [-0.5, -0.5],
                            "EndTag": [],
                            "EndOffset": [],
                            "Duration": "2~5"
                        }
                    ]
                },
                {
                    "Name": "RightUpArrow",
                    "Conditions": [
                        {
                            "Name": "",
                            "Allow": [
                                {
                                    "Name": "RightUpArrow",
                                    "Percent": 1.0,
                                    "Tags": [
                                        "Guider",
                                        "RightUpArrow"
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
                            "DecisionPeriod": 1000,
                            "StartTag": [
                                "RightUpArrow"
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
                    "Name": "LeftDownArrow",
                    "Conditions": [
                        {
                            "Name": "",
                            "Allow": [
                                {
                                    "Name": "LeftDownArrow",
                                    "Percent": 1.0,
                                    "Tags": [
                                        "Guider",
                                        "LeftDownArrow"
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
                            "DecisionPeriod": 1000,
                            "StartTag": [
                                "LeftDownArrow"
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
                    "Name": "RightDownArrow",
                    "Conditions": [
                        {
                            "Name": "",
                            "Allow": [
                                {
                                    "Name": "RightDownArrow",
                                    "Percent": 1.0,
                                    "Tags": [
                                        "Guider",
                                        "RightDownArrow"
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
                            "DecisionPeriod": 1000,
                            "StartTag": [
                                "RightDownArrow"
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
