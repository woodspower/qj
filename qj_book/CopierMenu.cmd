{
    "InferenceName": "CopierMenu",
    "InferenceFile": "/home/leo/qj/object_detection/data/CopierMenu/inference_ssd/frozen_inference_graph.pb",
    "LabelMapFile": "/home/leo/qj/object_detection/data/CopierMenu/pascal_label_map.pbtxt",
    "Sequence": [
        {
            "Name": "Select one submenu in Copier menu",
            "KeyBody": [
                {
                    "Name": "Select Copier Submenu",
                    "Conditions": {
                            "Jobs": {"Bookname": "CopierSubmenu"},
                            "Allow": {"Tags": ["CopierOff"]}
                    },
                    "Actions": [
                        {
                            "Command": "Click",
                            "DecisionPeriod": 5000,
                            "StartTag": ["CopierOff"]
                        },
                        {
                            "Name": "Reload image",
                            "Command": "Reload",
                            "PresetPeriod": 2000
                        }
                    ]
                }
            ]
        },
        {
            "Name": "Go and do jobs in Copier Submenu",
            "KeyBody": [
                {
                    "Name": "Goto Copier Submenu",
                    "Conditions": [
                        {
                            "Name": "",
                            "Allow": [
                                {
                                    "Name": "",
                                    "Percent": 1.0,
                                    "Tags": [
                                        "CopierOn"
                                    ]
                                }
                            ],
                            "Disallow": []
                        }
                    ],
                    "Actions": [
                        {
                            "Command": "Goto",
                            "BookName": "CopierSubmenu"
                        }
                    ]
                }
            ]
        }
]
}


