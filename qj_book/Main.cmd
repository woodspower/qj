{"Main":
[
{"Name":"1.MainGui_Task_ZhuXian",
"KeyBody":
    [
    {"Name":"",
     "Conditions":
        [
        {"Name":"",
         "Allow":
            [
            {"Name":"",
             "Percent":1.0,
             "Tags": ["Actor", "mVIPLevel", "mBag"]
            },
            {"Name":"",
             "Percent":0.6,
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
        {"Name":"",
         "Command":"Click",
         "DecisionPeriod":5000,
         "StartTag": ["tZhuXian"],
         "StartOffset": [0 ,0],
         "EndTag": [],
         "EndOffset": [],
         "Duration": "2~5"
        }
        ],
     "GoBack":
        [
        {"Name":"",
         "Interruptible": true,
         "DecisionPeriod": "5000",
         "StartTag": ["mGoBack"],
         "StartOffset": [0 ,0],
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


    





