{
    "Main": [
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
                            "Name": "P(-1/4w,1/2h)",
                            "Command": "Click",
                            "DecisionPeriod": 1000,
                            "StartTag": [
                                "LeftArrow"
                            ],
                            "StartOffset": [
                                -0.25,
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
                            "Name": "P(5/4w,1/2h)",
                            "Command": "Click",
                            "DecisionPeriod": 1000,
                            "StartTag": [
                                "RightArrow"
                            ],
                            "StartOffset": [
                                1.25,
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
                            "Name": "P(1/2w,-1/4h)",
                            "Command": "Click",
                            "DecisionPeriod": 1000,
                            "StartTag": [
                                "UpArrow"
                            ],
                            "StartOffset": [
                                0.5,
                                -0.25
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
                            "Name": "DownArrow",
                            "Command": "Click",
                            "DecisionPeriod": 1000,
                            "StartTag": [
                                "DownArrow"
                            ],
                            "StartOffset": [
                                0.5,
                                1.25
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
                            "Name": "P(0, 0)",
                            "Command": "Click",
                            "DecisionPeriod": 1000,
                            "StartTag": [
                                "LeftUpArrow"
                            ],
                            "StartOffset": [],
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
                            "Name": "P(1., 0)",
                            "Command": "Click",
                            "DecisionPeriod": 1000,
                            "StartTag": [
                                "RightUpArrow"
                            ],
                            "StartOffset": [
                                1.0,
                                0
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
                            "Name": "P(0, 1.)",
                            "Command": "Click",
                            "DecisionPeriod": 1000,
                            "StartTag": [
                                "LeftDownArrow"
                            ],
                            "StartOffset": [
                                0,
                                1.0
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
                            "Name": "P(1., 1.)",
                            "Command": "Click",
                            "DecisionPeriod": 1000,
                            "StartTag": [
                                "RightDownArrow"
                            ],
                            "StartOffset": [
                                1.0,
                                1.0
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
            "Name": "",
            "Conditions": [
                {
                    "Name": "",
                    "Allow": [
                        {
                            "Name": "",
                            "Percent": 1.0,
                            "Tags": [
                                "Actor",
                                "mVIPLevel",
                                "mBag"
                            ]
                        },
                        {
                            "Name": "",
                            "Percent": 0.6,
                            "Tags": [
                                "Actor",
                                "mVIPLevel",
                                "mBag",
                                "mTeam",
                                "mPowerScore",
                                "mBeStronger",
                                "mMIC",
                                "mChat",
                                "mBroadcast",
                                "mLock",
                                "mCamera",
                                "mRide",
                                "mFriend",
                                "mTimeState",
                                "mExpStat",
                                "mMap",
                                "mMail",
                                "mBlood",
                                "mMagic",
                                "mProfile",
                                "mTask",
                                "mTeamInfo",
                                "mTaskMajorInfo",
                                "mTaskOtherInfo",
                                "mHideTaskCtl",
                                "mActorLevel",
                                "gWonderActive",
                                "gFirstPayGift",
                                "gGift",
                                "gActive",
                                "gSocial",
                                "gOpenGift",
                                "gOpenParty",
                                "mKillState",
                                "gControlA"
                            ]
                        }
                    ],
                    "Disallow": []
                }
            ],
            "Actions": [
                {
                    "Name": "",
                    "Command": "Click",
                    "DecisionPeriod": 5000,
                    "StartTag": [
                        "tZhuXian"
                    ],
                    "StartOffset": [
                        0,
                        0
                    ],
                    "EndTag": [],
                    "EndOffset": [],
                    "Duration": "2~5"
                }
            ],
            "GoBack": [
                {
                    "Name": "",
                    "Interruptible": true,
                    "DecisionPeriod": "5000",
                    "StartTag": [
                        "mGoBack"
                    ],
                    "StartOffset": [
                        0,
                        0
                    ],
                    "EndTag": [],
                    "EndOffset": [],
                    "Duration": "2~5"
                }
            ]
        }
    ]
}
