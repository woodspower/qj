{
    "Name": "CopierSubmenu",
    "InferenceName": "CopierMenu",
    "Sequence": [
        {
        "Name": "S1: Select and start a task",
        "KeyBody": {
                "Conditions": { "Allow": {"Tags": "TaskName"} },
                "Actions": [
                    {
                        "Name":"A1: Find a task",
                        "Command": "Find",
                        "FocusArea": [0.4, 0, 0.6, 1],
                        "SubActions": {
                                "Name":"Quit task selected mode before judge",
                                "Command": "Click",
                                "StartOffset": [ 0, -0.5 ]
                            },
                        "JudgeConditions":{
                            "Allow": {"Tags": "TimesOn"},
                            "FocusArea": [0.4, 0, 0.6, 1]
                        }
                    },
                    {
                        "Name":"A2: Select the task",
                        "Command": "Click",
                        "FocusArea": [0.4, 0, 0.6, 1]
                    },
                    {
                        "Name":"A3: Choose task level",
                        "Command": "Click",
                        "StartTag": ["ModeNightmare","ModeDiffcult","ModeEasy"]
                    },
                    {
                        "Name":"A4: Start the task",
                        "Command": "Click",
                        "StartTag": "CopierGo"
                    }
                ]
            }
        }
    ]
}


