{
    "InferenceName": "CopierMenu",
    "Sequence": {
        "Name": "Goto one of submenu from Copier/DailyCopier/MonsterTower",
        "KeyBody": [
            {
                "Name": "Check Copier Submenu",
                "Conditions": {
                        "Jobs": {"Bookname": "CopierSubmenu"},
                        "Allow": {"Tags": ["CopierOff", "CopierOn"]}
                },
                "Actions": [
                    {   
                        "Name": "Turn CopierOff to CopierOn",
                        "Command": "Click",
                        "StartTag": "CopierOff",
                        "StopOnFail": "No" 
                    },
                    {
                        "Command": "Goto",
                        "StartTag": "CopierOn",
                        "BookName": "CopierSubmenu" 
                    }
                ]
            }
        ]
    }
}


