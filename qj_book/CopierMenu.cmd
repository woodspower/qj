{
    "InferenceName": "CopierMenu",
    "Sequence": {
        "Name": "Goto one of submenu from Copier/DailyCopier/MonsterTower",
        "KeyBody": [
            {
                "Name": "Try CopierSubmenu",
                "Conditions": {
                        "Jobs": {"Bookname": "CopierSubmenu"},
                        "Allow": {"Tags": ["CopierOff", "CopierOn"]}
                },
                "Actions": [
                    {   
                        "Name": "Select CopierSubmenu",
                        "Command": "Click"
                    },
                    {
                        "Command": "Goto",
                        "BookName": "CopierSubmenu" 
                    }
                ]
            },
            {
                "Name": "Try DailyCopierSubmenu",
                "Conditions": {
                        "Jobs": {"Bookname": "DailyCopierSubmenu"},
                        "Allow": {"Tags": ["CopierOff", "CopierOn"]}
                },
                "Actions": [
                    {   
                        "Name": "Select DailyCopierSubmenu",
                        "Command": "Click"
                    },
                    {
                        "Command": "Goto",
                        "BookName": "DailyCopierSubmenu" 
                    }
                ]
            },
            {
                "Name": "Try MonsterTowerSubmenu",
                "Conditions": {
                        "Jobs": {"Bookname": "MonsterTowerSubmenu"},
                        "Allow": {"Tags": ["CopierOff", "CopierOn"]}
                },
                "Actions": [
                    {   
                        "Name": "Select MonsterTowerSubmenu",
                        "Command": "Click"
                    },
                    {
                        "Command": "Goto",
                        "BookName": "MonsterTowerSubmenu" 
                    }
                ]
            }
        ]
    }
}


