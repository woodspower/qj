{"Index":
[
{"_comments": "",
 "Name":"1.GuiderGui",
 "KeyBody":
    [
    {"Name":"LeftArrow",
     "Conditions":
        [
        {"_comments": "",
         "Name":"LeftArrow",
         "Allow":
            [
            {"_comments": "",
             "Name":"Default",
             "Percent":1.0,
             "Tags": ["GuiderGui", "gLeftArrow"]
            }
            ],
         "Disallow":[]
        }
        ],
     "Actions":
        [
        {"_comments": "if arrow center is (Xc,Yc), radix is (Lx,Ly), pos is (Xc-1.1Lc, Yc)",
         "Name":"LeftArrow",
         "Command":"Click",
         "DecisionPeriod":5000,
         "StartTag": ["gLeftArrow"],
         "StartOffset": [-1.1 ,0],
         "EndTag": [],
         "EndOffset": [],
         "Duration": "2~5"
        }
        ]
    },
    {"Name":"RightArrow",
     "Conditions":
        [
        {"_comments": "",
         "Name":"",
         "Allow":
            [
            {"_comments": "",
             "Name":"",
             "Percent":1.0,
             "Tags": ["GuiderGui", "gRightArrow"]
            }
            ],
         "Disallow":[]
        }
        ],
     "Actions":
        [
        {"_comments": "if arrow center is (Xc,Yc), radix is (Lx,Ly), pos is (Xc+1.1Lc, Yc)",
         "Name":"RightArrow",
         "Command":"Click",
         "DecisionPeriod":5000,
         "StartTag": ["gRightArrow"],
         "StartOffset": [1.1 ,0],
         "EndTag": [],
         "EndOffset": [],
         "Duration": "2~5"
        }
        ]
    },
    {"Name":"UpArrow",
     "Conditions":
        [
        {"_comments": "",
         "Name":"",
         "Allow":
            [
            {"_comments": "",
             "Name":"UpArrow",
             "Percent":1.0,
             "Tags": ["GuiderGui", "gUpArrow"]
            }
            ],
         "Disallow":[]
        }
        ],
     "Actions":
        [
        {"_comments": "if arrow center is (Xc,Yc), radix is (Lx,Ly), pos is (Xc, Yc-1.1Ly)",
         "Name":"UpArrow",
         "Command":"Click",
         "DecisionPeriod":5000,
         "StartTag": ["gUpArrow"],
         "StartOffset": [0, -1.1],
         "EndTag": [],
         "EndOffset": [],
         "Duration": "2~5"
        }
        ]
    },
    {"Name":"DownArrow",
     "Conditions":
        [
        {"_comments": "",
         "Name":"",
         "Allow":
            [
            {"_comments": "",
             "Name":"DownArrow",
             "Percent":1.0,
             "Tags": ["GuiderGui", "gDownArrow"]
            }
            ],
         "Disallow":[]
        }
        ],
     "Actions":
        [
        {"_comments": "if arrow center is (Xc,Yc), radix is (Lx,Ly), pos is (Xc, Yc+1.1Ly)",
         "Name":"DownArrow",
         "Command":"Click",
         "DecisionPeriod":5000,
         "StartTag": ["gDownArrow"],
         "StartOffset": [0, 1.1],
         "EndTag": [],
         "EndOffset": [],
         "Duration": "2~5"
        }
        ]
    },
    {"Name":"LeftUpArrow",
     "Conditions":
        [
        {"_comments": "",
         "Name":"",
         "Allow":
            [
            {"_comments": "",
             "Name":"LeftUpArrow",
             "Percent":1.0,
             "Tags": ["GuiderGui", "gLeftUpArrow"]
            }
            ],
         "Disallow":[]
        }
        ],
     "Actions":
        [
        {"_comments": "if arrow center is (Xc,Yc), radix is (Lx,Ly), pos is (Xc-1.1Lc, Yc-1.1Ly)",
         "Name":"LeftUpArrow",
         "Command":"Click",
         "DecisionPeriod":5000,
         "StartTag": ["gLeftUpArrow"],
         "StartOffset": [-1.1 ,-1.1],
         "EndTag": [],
         "EndOffset": [],
         "Duration": "2~5"
        }
        ]
    },
    {"Name":"RightUpArrow",
     "Conditions":
        [
        {"_comments": "",
         "Name":"",
         "Allow":
            [
            {"_comments": "",
             "Name":"RightUpArrow",
             "Percent":1.0,
             "Tags": ["GuiderGui", "gRightUpArrow"]
            }
            ],
         "Disallow":[]
        }
        ],
     "Actions":
        [
        {"_comments": "if arrow center is (Xc,Yc), radix is (Lx,Ly), pos is (Xc+1.1Lc, Yc-1.1Ly)",
         "Name":"RightUpArrow",
         "Command":"Click",
         "DecisionPeriod":5000,
         "StartTag": ["gRightUpArrow"],
         "StartOffset": [1.1 ,-1.1],
         "EndTag": [],
         "EndOffset": [],
         "Duration": "2~5"
        }
        ]
    },
    {"Name":"LeftDownArrow",
     "Conditions":
        [
        {"_comments": "",
         "Name":"",
         "Allow":
            [
            {"_comments": "",
             "Name":"LeftDownArrow",
             "Percent":1.0,
             "Tags": ["GuiderGui", "gLeftDownArrow"]
            }
            ],
         "Disallow":[]
        }
        ],
     "Actions":
        [
        {"_comments": "if arrow center is (Xc,Yc), radix is (Lx,Ly), pos is (Xc-1.1Lx, Yc+1.1Ly)",
         "Name":"LeftDownArrow",
         "Command":"Click",
         "DecisionPeriod":5000,
         "StartTag": ["gLeftDownArrow"],
         "StartOffset": [-1.1, 1.1],
         "EndTag": [],
         "EndOffset": [],
         "Duration": "2~5"
        }
        ]
    },
    {"Name":"RightDownArrow",
     "Conditions":
        [
        {"_comments": "",
         "Name":"",
         "Allow":
            [
            {"_comments": "",
             "Name":"RightDownArrow",
             "Percent":1.0,
             "Tags": ["GuiderGui", "gRightDownArrow"]
            }
            ],
         "Disallow":[]
        }
        ],
     "Actions":
        [
        {"_comments": "if arrow center is (Xc,Yc), radix is (Lx,Ly), pos is (Xc+1.1Lx, Yc+1.1Ly)",
         "Name":"RightDownArrow",
         "Command":"Click",
         "DecisionPeriod":5000,
         "StartTag": ["gRightDownArrow"],
         "StartOffset": [1.1, 1.1],
         "EndTag": [],
         "EndOffset": [],
         "Duration": "2~5"
        }
        ]
    }
    ]
},

{"_comments": "",
"Name":"2.MainGui",
"KeyBody":
    [
    {"_comments": "",
     "Name":"Default",
     "Conditions":
        [
        {"_comments": "",
         "Name":"OffenObject",
         "Allow":
            [
            {"_comments": "",
             "Name":"Actor+VIP+Bag",
             "Percent":1.0,
             "Tags": ["Actor", "mVIPLevel", "mBag"]
            },
            {"_comments": "",
             "Name":"60%OffenObject",
             "Percent":0.3,
             "Tags": ["Actor", "mVIPLevel", "mBag", 
                      "mTeam", "mPowerScore", "mBeStronger", "mMIC", "mChat",
                      "mBroadcast", "mLock", "mCamera", "mRide", "mFriend", "mTimeState",
                      "mExpStat", "mMap", "mMail", "mBlood", "mMagic", "mProfile", "mTask",
                      "mTeamInfo", "mTaskMajorInfo", "mTaskOtherInfo", "mHideTaskCtl",
                      "mActorLevel", "gWonderActive", "gFirstPayGift", "gGift", "gActive",
                      "gSocial", "gOpenGift", "gOpenParty", "mKillState", "gControlA"]
            }
            ],
         "Disallow":[]
        }
        ],
     "Actions":
        [
        {"_comments": "",
         "Name":"GotoMainLoop",
         "Command":"Goto",
         "DecisionPeriod":0,
         "BookName": "MainLoop"
        }
        ]
    }
    ]
},

{"_comments": "",
"Name":"3.DialogGui",
"KeyBody":
    [
    {"_comments": "",
     "Name":"Default",
     "Conditions":
        [
        {"_comments": "",
         "Name":"",
         "Allow":
            [
            {"_comments": "",
             "Name":"Dialog+Confirm",
             "Percent":1.0,
             "Tags": ["DialogGui", "dConfirm"]
            },
            {"_comments": "",
             "Name":"Dialog+Next",
             "Percent":1.0,
             "Tags": ["DialogGui", "dNext"]
            },
            {"_comments": "",
             "Name":"Movie+Confirm",
             "Percent":1.0,
             "Tags": ["MovieGui", "dConfirm"]
            },
            {"_comments": "",
             "Name":"Movie+Next",
             "Percent":1.0,
             "Tags": ["MovieGui", "dNext"]
            }
            ],
         "Disallow":[]
        }
        ],
     "Actions":
        [
        {"_comments": "",
         "Name":"ClickNextORConfirm",
         "Command":"Click",
         "DecisionPeriod":5000,
         "StartTag": ["dConfirm", "dNext"],
         "StartOffset": [0 ,0],
         "EndTag": [],
         "EndOffset": [0 ,0],
         "Duration": "2~5"
        }
        ]
    }
    ]
}
]
}

