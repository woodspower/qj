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
                        "SelectToArea": [0.4, 0, 0.6, 1],
                        "PostloadTime": 1000,
                        "SubActions": {
                                "Name":"Quit task selected mode before judge",
                                "Command": "Click",
                                "PostloadTime": 1000,
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
                        "PostloadTime": 1000,
                        "SelectToArea": [0.4, 0, 0.6, 1]
                    },
                    {
                        "Name":"A3: Start the task",
                        "Command": "Click",
                        "StartTag": "CopierGo",
                        "PostloadTime": 1000
                    }
                ]
            }
        },
        {
            "Name": "S2: Gernal confirmation",
            "KeyBody": {
                "Conditions": { 
                    "Allow": {"Tags": ["iConfirm", "iCancel", "iReject"]} 
                },
                "Actions": { "Command": "Click" }
            }
        }
    ]
}


