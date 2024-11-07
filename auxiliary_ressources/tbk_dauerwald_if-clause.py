# This document contains definitions / code for the Dauerwald Code (attribute and labels)
# for reference older versions are included

###  ----------------------  ###
def TODO:
###  ----------------------  ###
- check whether VegZone vorhanden, ansonsten default to KL

###  ----------------------  ###
def --#--- INFO -----:
###  ----------------------  ###
# quick overview of Dauerwaldcode categories 
# with distinction between Vegetation Height zones

if("VegZone_Code" IN (-1, 0, 1, 2, 4, 5), 
    # collin/sub-/untermontan/no category (-1, 0, 1)
    '',
    if ("VegZone_Code" IN (6, 7),
        # Obermontan
        '',
        if("VegZone_Code" IN (8),
            # Hochmontan
            '',
            # Subalpin
            ''
        )
    )
)

Kollin/Sub-/Untermontan (KL,SM,UM): NH 10/18/26 | LH 9/16/23
Obermontan (OM): NH 9/16/23 | LH 7/13/19
Hochmontan (HM): NH 7/13/19 | LH 6/11/16
Subalpin (SA): NH 6 /11/16 | LH 5/9/13






###  ----------------------  ###
def --#--- CALC DW_CODE -----:
###  ----------------------  ###
# these calculations provide the logic to determine the DW_Code (Nr -1 to 5)
# which can then be used to apply a symbology


###  ----------------------  ###
def -#--- v2 NH/LH Distinction:
###  ----------------------  ###
# Basic Dauerwaldcode with distinction between NH/LH
# no comments contained
# usable for copy paste into QGIS expression editor

if("NH">50,
    if("hdom">=28, 
        if("DG_os" + "DG_ueb" >= 45, 
            if("DG_ms" >= 35,
            4,
                if("DG_ms">=25,
                    if("DG_us" + "DG_ks">=20,
                        3,
                        2
                    ),
                    if("DG_ms">=15,
                        if("DG_us"+ "DG_ks">=10,
                            2,
                            1
                        ),
                        if("DG_us"+"DG_ks">=10,
                            1,
                            0
                        )
                    )
                )
            ),
            5
        ), 
        if("hdom">20,
            -1, 
            if("hdom">10,
                -2,
                -3
            )
        )
    ),
    if("hdom">=25, 
        if("DG_os" + "DG_ueb" >= 45, 
            if("DG_ms" >= 35,
                4,
                if("DG_ms">=25,
                    if("DG_us" + "DG_ks">=20,
                        3,
                        2
                    ),
                    if("DG_ms">=15,
                        if("DG_us"+ "DG_ks">=10,
                            2,
                            1
                        ),
                        if("DG_us"+"DG_ks">=10,
                            1,
                            0
                        )
                    )
                )
            ),
        5), 
        if("hdom">18,
            -1, 
            if("hdom">10,
                -2,
                -3
            )
        )
    )
)
###  ----------------------  ###

###  ----------------------  ###
def -#--- v3 Structure VegZone Distinction:
###  ----------------------  ###
# quick overview of Dauerwaldcode categories 
# with distinction between Vegetation Height zones

if("VegZone" IN (-1, 2, 4, 5), 
    # collin/sub-/untermontan/no category
    '',
    if ("VegZone_Code" IN (6, 7),
        # Obermontan
        '',
        if("VegZone_Code" IN (8),
            # Hochmontan
            '',
            # Subalpin
            ''
        )
    )
)
 
###  ----------------------  ###


###  ----------------------  ###
def -#--- v3 VegZone Distinction:
###  ----------------------  ###
# Dauerwaldcode categories 
# with distinction between Vegetation Height zones
# no comments contained
# usable for copy paste into QGIS expression editor

if("VegZone" IN (-1, 2, 4, 5), 
    if("NH">50,
        if("hdom">=28, 
            if("DG_os" + "DG_ueb" >= 45, 
                if("DG_ms" >= 35,
                4,
                    if("DG_ms">=25,
                        if("DG_us" + "DG_ks">=20,
                            3,
                            2
                        ),
                        if("DG_ms">=15,
                            if("DG_us"+ "DG_ks">=10,
                                2,
                                1
                            ),
                            if("DG_us"+"DG_ks">=10,
                                1,
                                0
                            )
                        )
                    )
                ),
                5
            ), 
            if("hdom">20,
                -1, 
                if("hdom">10,
                    -2,
                    -3
                )
            )
        ),
        if("hdom">=25, 
            if("DG_os" + "DG_ueb" >= 45, 
                if("DG_ms" >= 35,
                    4,
                    if("DG_ms">=25,
                        if("DG_us" + "DG_ks">=20,
                            3,
                            2
                        ),
                        if("DG_ms">=15,
                            if("DG_us"+ "DG_ks">=10,
                                2,
                                1
                            ),
                            if("DG_us"+"DG_ks">=10,
                                1,
                                0
                            )
                        )
                    )
                ),
            5), 
            if("hdom">18,
                -1, 
                if("hdom">10,
                    -2,
                    -3
                )
            )
        )
    ),
    if ("VegZone_Code" IN (6, 7),
        if("NH">50,
            if("hdom">=25, 
                if("DG_os" + "DG_ueb" >= 45, 
                    if("DG_ms" >= 35,
                    4,
                        if("DG_ms">=25,
                            if("DG_us" + "DG_ks">=20,
                                3,
                                2
                            ),
                            if("DG_ms">=15,
                                if("DG_us"+ "DG_ks">=10,
                                    2,
                                    1
                                ),
                                if("DG_us"+"DG_ks">=10,
                                    1,
                                    0
                                )
                            )
                        )
                    ),
                    5
                ), 
                if("hdom">18,
                    -1, 
                    if("hdom">10,
                        -2,
                        -3
                    )
                )
            ),
            if("hdom">=21, 
                if("DG_os" + "DG_ueb" >= 45, 
                    if("DG_ms" >= 35,
                        4,
                        if("DG_ms">=25,
                            if("DG_us" + "DG_ks">=20,
                                3,
                                2
                            ),
                            if("DG_ms">=15,
                                if("DG_us"+ "DG_ks">=10,
                                    2,
                                    1
                                ),
                                if("DG_us"+"DG_ks">=10,
                                    1,
                                    0
                                )
                            )
                        )
                    ),
                5), 
                if("hdom">15,
                    -1, 
                    if("hdom">9,
                        -2,
                        -3
                    )
                )
            )
        ),
        if("VegZone_Code" IN (8),
            if("NH">50,
                if("hdom">=21, 
                    if("DG_os" + "DG_ueb" >= 45, 
                        if("DG_ms" >= 35,
                        4,
                            if("DG_ms">=25,
                                if("DG_us" + "DG_ks">=20,
                                    3,
                                    2
                                ),
                                if("DG_ms">=15,
                                    if("DG_us"+ "DG_ks">=10,
                                        2,
                                        1
                                    ),
                                    if("DG_us"+"DG_ks">=10,
                                        1,
                                        0
                                    )
                                )
                            )
                        ),
                        5
                    ), 
                    if("hdom">15,
                        -1, 
                        if("hdom">9,
                            -2,
                            -3
                        )
                    )
                ),
                if("hdom">=18, 
                    if("DG_os" + "DG_ueb" >= 45, 
                        if("DG_ms" >= 35,
                            4,
                            if("DG_ms">=25,
                                if("DG_us" + "DG_ks">=20,
                                    3,
                                    2
                                ),
                                if("DG_ms">=15,
                                    if("DG_us"+ "DG_ks">=10,
                                        2,
                                        1
                                    ),
                                    if("DG_us"+"DG_ks">=10,
                                        1,
                                        0
                                    )
                                )
                            )
                        ),
                    5), 
                    if("hdom">13,
                        -1, 
                        if("hdom">8,
                            -2,
                            -3
                        )
                    )
                )
            ),
            if("NH">50,
                if("hdom">=18, 
                    if("DG_os" + "DG_ueb" >= 45, 
                        if("DG_ms" >= 35,
                        4,
                            if("DG_ms">=25,
                                if("DG_us" + "DG_ks">=20,
                                    3,
                                    2
                                ),
                                if("DG_ms">=15,
                                    if("DG_us"+ "DG_ks">=10,
                                        2,
                                        1
                                    ),
                                    if("DG_us"+"DG_ks">=10,
                                        1,
                                        0
                                    )
                                )
                            )
                        ),
                        5
                    ), 
                    if("hdom">13,
                        -1, 
                        if("hdom">8,
                            -2,
                            -3
                        )
                    )
                ),
                if("hdom">=15, 
                    if("DG_os" + "DG_ueb" >= 45, 
                        if("DG_ms" >= 35,
                            4,
                            if("DG_ms">=25,
                                if("DG_us" + "DG_ks">=20,
                                    3,
                                    2
                                ),
                                if("DG_ms">=15,
                                    if("DG_us"+ "DG_ks">=10,
                                        2,
                                        1
                                    ),
                                    if("DG_us"+"DG_ks">=10,
                                        1,
                                        0
                                    )
                                )
                            )
                        ),
                    5), 
                    if("hdom">10,
                        -1, 
                        if("hdom">7,
                            -2,
                            -3
                        )
                    )
                )
            )
        )
    )
)




###  ----------------------  ###
def -#--- v3 VegZone Distinction without ks:
###  ----------------------  ###
# Dauerwaldcode categories 
# with distinction between Vegetation Height zones
# no comments contained
# usable for copy paste into QGIS expression editor

if("VegZone" IN (-1, 2, 4, 5), 
    if("NH">50,
        if("hdom">=28, 
            if("DG_os" + "DG_ueb" >= 45, 
                if("DG_ms" >= 35,
                4,
                    if("DG_ms">=25,
                        if("DG_us" >=20,
                            3,
                            2
                        ),
                        if("DG_ms">=15,
                            if("DG_us">=10,
                                2,
                                1
                            ),
                            if("DG_us">=10,
                                1,
                                0
                            )
                        )
                    )
                ),
                5
            ), 
            if("hdom">20,
                -1, 
                if("hdom">10,
                    -2,
                    -3
                )
            )
        ),
        if("hdom">=25, 
            if("DG_os" + "DG_ueb" >= 45, 
                if("DG_ms" >= 35,
                    4,
                    if("DG_ms">=25,
                        if("DG_us" >=20,
                            3,
                            2
                        ),
                        if("DG_ms">=15,
                            if("DG_us">=10,
                                2,
                                1
                            ),
                            if("DG_us">=10,
                                1,
                                0
                            )
                        )
                    )
                ),
            5), 
            if("hdom">18,
                -1, 
                if("hdom">10,
                    -2,
                    -3
                )
            )
        )
    ),
    if ("VegZone_Code" IN (6, 7),
        if("NH">50,
            if("hdom">=25, 
                if("DG_os" + "DG_ueb" >= 45, 
                    if("DG_ms" >= 35,
                    4,
                        if("DG_ms">=25,
                            if("DG_us" >=20,
                                3,
                                2
                            ),
                            if("DG_ms">=15,
                                if("DG_us">=10,
                                    2,
                                    1
                                ),
                                if("DG_us">=10,
                                    1,
                                    0
                                )
                            )
                        )
                    ),
                    5
                ), 
                if("hdom">18,
                    -1, 
                    if("hdom">10,
                        -2,
                        -3
                    )
                )
            ),
            if("hdom">=21, 
                if("DG_os" + "DG_ueb" >= 45, 
                    if("DG_ms" >= 35,
                        4,
                        if("DG_ms">=25,
                            if("DG_us" >=20,
                                3,
                                2
                            ),
                            if("DG_ms">=15,
                                if("DG_us">=10,
                                    2,
                                    1
                                ),
                                if("DG_us">=10,
                                    1,
                                    0
                                )
                            )
                        )
                    ),
                5), 
                if("hdom">15,
                    -1, 
                    if("hdom">9,
                        -2,
                        -3
                    )
                )
            )
        ),
        if("VegZone_Code" IN (8),
            if("NH">50,
                if("hdom">=21, 
                    if("DG_os" + "DG_ueb" >= 45, 
                        if("DG_ms" >= 35,
                        4,
                            if("DG_ms">=25,
                                if("DG_us" >=20,
                                    3,
                                    2
                                ),
                                if("DG_ms">=15,
                                    if("DG_us">=10,
                                        2,
                                        1
                                    ),
                                    if("DG_us">=10,
                                        1,
                                        0
                                    )
                                )
                            )
                        ),
                        5
                    ), 
                    if("hdom">15,
                        -1, 
                        if("hdom">9,
                            -2,
                            -3
                        )
                    )
                ),
                if("hdom">=18, 
                    if("DG_os" + "DG_ueb" >= 45, 
                        if("DG_ms" >= 35,
                            4,
                            if("DG_ms">=25,
                                if("DG_us" >=20,
                                    3,
                                    2
                                ),
                                if("DG_ms">=15,
                                    if("DG_us">=10,
                                        2,
                                        1
                                    ),
                                    if("DG_us">=10,
                                        1,
                                        0
                                    )
                                )
                            )
                        ),
                    5), 
                    if("hdom">13,
                        -1, 
                        if("hdom">8,
                            -2,
                            -3
                        )
                    )
                )
            ),
            if("NH">50,
                if("hdom">=18, 
                    if("DG_os" + "DG_ueb" >= 45, 
                        if("DG_ms" >= 35,
                        4,
                            if("DG_ms">=25,
                                if("DG_us" >=20,
                                    3,
                                    2
                                ),
                                if("DG_ms">=15,
                                    if("DG_us">=10,
                                        2,
                                        1
                                    ),
                                    if("DG_us">=10,
                                        1,
                                        0
                                    )
                                )
                            )
                        ),
                        5
                    ), 
                    if("hdom">13,
                        -1, 
                        if("hdom">8,
                            -2,
                            -3
                        )
                    )
                ),
                if("hdom">=15, 
                    if("DG_os" + "DG_ueb" >= 45, 
                        if("DG_ms" >= 35,
                            4,
                            if("DG_ms">=25,
                                if("DG_us" >=20,
                                    3,
                                    2
                                ),
                                if("DG_ms">=15,
                                    if("DG_us">=10,
                                        2,
                                        1
                                    ),
                                    if("DG_us">=10,
                                        1,
                                        0
                                    )
                                )
                            )
                        ),
                    5), 
                    if("hdom">10,
                        -1, 
                        if("hdom">7,
                            -2,
                            -3
                        )
                    )
                )
            )
        )
    )
)





###  ----------------------  ###
def -#--- v4 VegZone Distinction 2023-12-20 without ks:
###  ----------------------  ###
# Dauerwaldcode categories 
# with distinction between Vegetation Height zones
# no comments contained
# usable for copy paste into QGIS expression editor

if("VegZone_Code" IN (-1, 0, 1, 2, 4, 5), 
    if("NH">50,
        if("hdom">=26, 
            if("DG_os" + "DG_ueb" >= 45, 
                if("DG_ms" >= 35,
                4,
                    if("DG_ms">=25,
                        if("DG_us" >=20,
                            3,
                            2
                        ),
                        if("DG_ms">=15,
                            if("DG_us">=10,
                                2,
                                1
                            ),
                            if("DG_us">=10,
                                1,
                                0
                            )
                        )
                    )
                ),
                5
            ), 
            if("hdom">18,
                -1, 
                if("hdom">10,
                    -2,
                    -3
                )
            )
        ),
        if("hdom">=23, 
            if("DG_os" + "DG_ueb" >= 45, 
                if("DG_ms" >= 35,
                    4,
                    if("DG_ms">=25,
                        if("DG_us" >=20,
                            3,
                            2
                        ),
                        if("DG_ms">=15,
                            if("DG_us">=10,
                                2,
                                1
                            ),
                            if("DG_us">=10,
                                1,
                                0
                            )
                        )
                    )
                ),
            5), 
            if("hdom">16,
                -1, 
                if("hdom">9,
                    -2,
                    -3
                )
            )
        )
    ),
    if ("VegZone_Code" IN (6, 7),
        if("NH">50,
            if("hdom">=23, 
                if("DG_os" + "DG_ueb" >= 45, 
                    if("DG_ms" >= 35,
                    4,
                        if("DG_ms">=25,
                            if("DG_us" >=20,
                                3,
                                2
                            ),
                            if("DG_ms">=15,
                                if("DG_us">=10,
                                    2,
                                    1
                                ),
                                if("DG_us">=10,
                                    1,
                                    0
                                )
                            )
                        )
                    ),
                    5
                ), 
                if("hdom">16,
                    -1, 
                    if("hdom">9,
                        -2,
                        -3
                    )
                )
            ),
            if("hdom">=19, 
                if("DG_os" + "DG_ueb" >= 45, 
                    if("DG_ms" >= 35,
                        4,
                        if("DG_ms">=25,
                            if("DG_us" >=20,
                                3,
                                2
                            ),
                            if("DG_ms">=15,
                                if("DG_us">=10,
                                    2,
                                    1
                                ),
                                if("DG_us">=10,
                                    1,
                                    0
                                )
                            )
                        )
                    ),
                5), 
                if("hdom">13,
                    -1, 
                    if("hdom">7,
                        -2,
                        -3
                    )
                )
            )
        ),
        if("VegZone_Code" IN (8),
            if("NH">50,
                if("hdom">=19, 
                    if("DG_os" + "DG_ueb" >= 45, 
                        if("DG_ms" >= 35,
                        4,
                            if("DG_ms">=25,
                                if("DG_us" >=20,
                                    3,
                                    2
                                ),
                                if("DG_ms">=15,
                                    if("DG_us">=10,
                                        2,
                                        1
                                    ),
                                    if("DG_us">=10,
                                        1,
                                        0
                                    )
                                )
                            )
                        ),
                        5
                    ), 
                    if("hdom">13,
                        -1, 
                        if("hdom">7,
                            -2,
                            -3
                        )
                    )
                ),
                if("hdom">=16, 
                    if("DG_os" + "DG_ueb" >= 45, 
                        if("DG_ms" >= 35,
                            4,
                            if("DG_ms">=25,
                                if("DG_us" >=20,
                                    3,
                                    2
                                ),
                                if("DG_ms">=15,
                                    if("DG_us">=10,
                                        2,
                                        1
                                    ),
                                    if("DG_us">=10,
                                        1,
                                        0
                                    )
                                )
                            )
                        ),
                    5), 
                    if("hdom">11,
                        -1, 
                        if("hdom">6,
                            -2,
                            -3
                        )
                    )
                )
            ),
            if("NH">50,
                if("hdom">=16, 
                    if("DG_os" + "DG_ueb" >= 45, 
                        if("DG_ms" >= 35,
                        4,
                            if("DG_ms">=25,
                                if("DG_us" >=20,
                                    3,
                                    2
                                ),
                                if("DG_ms">=15,
                                    if("DG_us">=10,
                                        2,
                                        1
                                    ),
                                    if("DG_us">=10,
                                        1,
                                        0
                                    )
                                )
                            )
                        ),
                        5
                    ), 
                    if("hdom">11,
                        -1, 
                        if("hdom">6,
                            -2,
                            -3
                        )
                    )
                ),
                if("hdom">=13, 
                    if("DG_os" + "DG_ueb" >= 45, 
                        if("DG_ms" >= 35,
                            4,
                            if("DG_ms">=25,
                                if("DG_us" >=20,
                                    3,
                                    2
                                ),
                                if("DG_ms">=15,
                                    if("DG_us">=10,
                                        2,
                                        1
                                    ),
                                    if("DG_us">=10,
                                        1,
                                        0
                                    )
                                )
                            )
                        ),
                    5), 
                    if("hdom">9,
                        -1, 
                        if("hdom">5,
                            -2,
                            -3
                        )
                    )
                )
            )
        )
    )
)



###  ----------------------  ###
def -#--- v5 VegZone Distinction 2024-06-17 without ks hotfix bug :
###  ----------------------  ###
# Dauerwaldcode categories
# with distinction between Vegetation Height zones
# no comments contained
# usable for copy paste into QGIS expression editor
# solved hdom bug that

if("VegZone_Code" IN (-1, 0, 1, 2, 4, 5),
    if("NH">50,
        if("hdom">=26,
            if("DG_os" + "DG_ueb" >= 45,
                if("DG_ms" >= 35,
                4,
                    if("DG_ms">=25,
                        if("DG_us" >=20,
                            3,
                            2
                        ),
                        if("DG_ms">=15,
                            if("DG_us">=10,
                                2,
                                1
                            ),
                            if("DG_us">=10,
                                1,
                                0
                            )
                        )
                    )
                ),
                5
            ),
            if("hdom">18,
                -1,
                if("hdom">10,
                    -2,
                    -3
                )
            )
        ),
        if("hdom">=23,
            if("DG_os" + "DG_ueb" >= 45,
                if("DG_ms" >= 35,
                    4,
                    if("DG_ms">=25,
                        if("DG_us" >=20,
                            3,
                            2
                        ),
                        if("DG_ms">=15,
                            if("DG_us">=10,
                                2,
                                1
                            ),
                            if("DG_us">=10,
                                1,
                                0
                            )
                        )
                    )
                ),
            5),
            if("hdom">16,
                -1,
                if("hdom">9,
                    -2,
                    -3
                )
            )
        )
    ),
    if ("VegZone_Code" IN (6, 7),
        if("NH">50,
            if("hdom">=23,
                if("DG_os" + "DG_ueb" >= 45,
                    if("DG_ms" >= 35,
                    4,
                        if("DG_ms">=25,
                            if("DG_us" >=20,
                                3,
                                2
                            ),
                            if("DG_ms">=15,
                                if("DG_us">=10,
                                    2,
                                    1
                                ),
                                if("DG_us">=10,
                                    1,
                                    0
                                )
                            )
                        )
                    ),
                    5
                ),
                if("hdom">16,
                    -1,
                    if("hdom">9,
                        -2,
                        -3
                    )
                )
            ),
            if("hdom">=19,
                if("DG_os" + "DG_ueb" >= 45,
                    if("DG_ms" >= 35,
                        4,
                        if("DG_ms">=25,
                            if("DG_us" >=20,
                                3,
                                2
                            ),
                            if("DG_ms">=15,
                                if("DG_us">=10,
                                    2,
                                    1
                                ),
                                if("DG_us">=10,
                                    1,
                                    0
                                )
                            )
                        )
                    ),
                5),
                if("hdom">13,
                    -1,
                    if("hdom">7,
                        -2,
                        -3
                    )
                )
            )
        ),
        if("VegZone_Code" IN (8),
            if("NH">50,
                if("hdom">=19,
                    if("DG_os" + "DG_ueb" >= 45,
                        if("DG_ms" >= 35,
                        4,
                            if("DG_ms">=25,
                                if("DG_us" >=20,
                                    3,
                                    2
                                ),
                                if("DG_ms">=15,
                                    if("DG_us">=10,
                                        2,
                                        1
                                    ),
                                    if("DG_us">=10,
                                        1,
                                        0
                                    )
                                )
                            )
                        ),
                        5
                    ),
                    if("hdom">13,
                        -1,
                        if("hdom">7,
                            -2,
                            -3
                        )
                    )
                ),
                if("hdom">=16,
                    if("DG_os" + "DG_ueb" >= 45,
                        if("DG_ms" >= 35,
                            4,
                            if("DG_ms">=25,
                                if("DG_us" >=20,
                                    3,
                                    2
                                ),
                                if("DG_ms">=15,
                                    if("DG_us">=10,
                                        2,
                                        1
                                    ),
                                    if("DG_us">=10,
                                        1,
                                        0
                                    )
                                )
                            )
                        ),
                    5),
                    if("hdom">11,
                        -1,
                        if("hdom">6,
                            -2,
                            -3
                        )
                    )
                )
            ),
            if("NH">50,
                if("hdom">=16,
                    if("DG_os" + "DG_ueb" >= 45,
                        if("DG_ms" >= 35,
                        4,
                            if("DG_ms">=25,
                                if("DG_us" >=20,
                                    3,
                                    2
                                ),
                                if("DG_ms">=15,
                                    if("DG_us">=10,
                                        2,
                                        1
                                    ),
                                    if("DG_us">=10,
                                        1,
                                        0
                                    )
                                )
                            )
                        ),
                        5
                    ),
                    if("hdom">11,
                        -1,
                        if("hdom">6,
                            -2,
                            -3
                        )
                    )
                ),
                if("hdom">=13,
                    if("DG_os" + "DG_ueb" >= 45,
                        if("DG_ms" >= 35,
                            4,
                            if("DG_ms">=25,
                                if("DG_us" >=20,
                                    3,
                                    2
                                ),
                                if("DG_ms">=15,
                                    if("DG_us">=10,
                                        2,
                                        1
                                    ),
                                    if("DG_us">=10,
                                        1,
                                        0
                                    )
                                )
                            )
                        ),
                    5),
                    if("hdom">9,
                        -1,
                        if("hdom">5,
                            -2,
                            -3
                        )
                    )
                )
            )
        )
    )
)





###  ----------------------  ###
def --#--- LABELS DW_Code -----:
###  ----------------------  ###

###  ----------------------  ###
def -#--- v1/2 Dauerwald Labels:
###  ----------------------  ###
to_string("hdom") + '.' + 

to_string(if("NH"<50,if("hdom">=25, if("DG_os" + "DG_ueb" >= 45, if("DG_ms" >= 35,4,if("DG_ms">=25,if("DG_us" + "DG_ks">=20,3,2),if("DG_ms">=15,if("DG_us"+ "DG_ks">=10,2,1),if("DG_us"+"DG_ks">=10,1,0)))),5), if("hdom">18,-1,if("hdom">10,-2,-3))),if("hdom">=28, if("DG_os" + "DG_ueb" >= 45, if("DG_ms" >= 35,4,if("DG_ms">=25,if("DG_us" + "DG_ks">=20,3,2),if("DG_ms">=15,if("DG_us"+ "DG_ks">=10,2,1),if("DG_us"+"DG_ks">=10,1,0)))),5), if("hdom">20,-1,if("hdom">10,-2,-3))))) + '.' + 

to_string(if("DG_os" + "DG_ueb" < 35, 5, if("DG_os" + "DG_ueb" <45, 4, if("DG_os" + "DG_ueb" <= 55, 3, if("DG_os" + "DG_ueb" < 70, 2, if("DG_os" + "DG_ueb" < 85, 1, 0)))))) + 

to_string(if("DG_ms" > 45, 5, if("DG_ms" > 35, 4, if("DG_ms" >= 25, 3, if("DG_ms" >= 15, 2, if("DG_ms" >= 5, 1, 0)))))) + 

to_string(if("DG_us" + "DG_ks" > 40, 5, if("DG_us" + "DG_ks" > 30, 4, if("DG_us" + "DG_ks" >= 20, 3, if("DG_us" + "DG_ks" >= 10, 2, if("DG_us" + "DG_ks" > 1, 1, 0))))))
 
+ '\n' + 
to_string("DG_os" + "DG_ueb") + '.' + 
to_string("DG_ms") + '.' + 
to_string("DG_us"+ "DG_ks")



###  ----------------------  ###
def -#--- v3 Dauerwald Labels VegZone:
###  ----------------------  ###


if("VegZone_Code" IN (-1, 2), 
    'K',
    if("VegZone_Code" IN (4),
        'SM',
        if("VegZone_Code" IN (5),
            'UM',
            if("VegZone_Code" IN (6, 7),
                'OM',
                if("VegZone_Code" IN (8),
                    'HM',
                     if("VegZone_Code" IN (9),
                    'SA',
                    '??'
                    )
                )
            )
        )    
    )
) + to_string("hdom") + '.' + 

to_string(to_int(round(to_real("NH")/10))) + 

'(' + 

to_string(if("VegZone_Code" IN (-1, 2, 4, 5), 
    if("NH">50,
        if("hdom">=28, 
            if("DG_os" + "DG_ueb" >= 45, 
                if("DG_ms" >= 35,
                4,
                    if("DG_ms">=25,
                        if("DG_us" + "DG_ks">=20,
                            3,
                            2
                        ),
                        if("DG_ms">=15,
                            if("DG_us"+ "DG_ks">=10,
                                2,
                                1
                            ),
                            if("DG_us"+"DG_ks">=10,
                                1,
                                0
                            )
                        )
                    )
                ),
                5
            ), 
            if("hdom">20,
                -1, 
                if("hdom">10,
                    -2,
                    -3
                )
            )
        ),
        if("hdom">=25, 
            if("DG_os" + "DG_ueb" >= 45, 
                if("DG_ms" >= 35,
                    4,
                    if("DG_ms">=25,
                        if("DG_us" + "DG_ks">=20,
                            3,
                            2
                        ),
                        if("DG_ms">=15,
                            if("DG_us"+ "DG_ks">=10,
                                2,
                                1
                            ),
                            if("DG_us"+"DG_ks">=10,
                                1,
                                0
                            )
                        )
                    )
                ),
            5), 
            if("hdom">18,
                -1, 
                if("hdom">10,
                    -2,
                    -3
                )
            )
        )
    ),
    if ("VegZone_Code" IN (6, 7),
        if("NH">50,
            if("hdom">=25, 
                if("DG_os" + "DG_ueb" >= 45, 
                    if("DG_ms" >= 35,
                    4,
                        if("DG_ms">=25,
                            if("DG_us" + "DG_ks">=20,
                                3,
                                2
                            ),
                            if("DG_ms">=15,
                                if("DG_us"+ "DG_ks">=10,
                                    2,
                                    1
                                ),
                                if("DG_us"+"DG_ks">=10,
                                    1,
                                    0
                                )
                            )
                        )
                    ),
                    5
                ), 
                if("hdom">18,
                    -1, 
                    if("hdom">10,
                        -2,
                        -3
                    )
                )
            ),
            if("hdom">=21, 
                if("DG_os" + "DG_ueb" >= 45, 
                    if("DG_ms" >= 35,
                        4,
                        if("DG_ms">=25,
                            if("DG_us" + "DG_ks">=20,
                                3,
                                2
                            ),
                            if("DG_ms">=15,
                                if("DG_us"+ "DG_ks">=10,
                                    2,
                                    1
                                ),
                                if("DG_us"+"DG_ks">=10,
                                    1,
                                    0
                                )
                            )
                        )
                    ),
                5), 
                if("hdom">15,
                    -1, 
                    if("hdom">9,
                        -2,
                        -3
                    )
                )
            )
        ),
        if("VegZone_Code" IN (8),
            if("NH">50,
                if("hdom">=21, 
                    if("DG_os" + "DG_ueb" >= 45, 
                        if("DG_ms" >= 35,
                        4,
                            if("DG_ms">=25,
                                if("DG_us" + "DG_ks">=20,
                                    3,
                                    2
                                ),
                                if("DG_ms">=15,
                                    if("DG_us"+ "DG_ks">=10,
                                        2,
                                        1
                                    ),
                                    if("DG_us"+"DG_ks">=10,
                                        1,
                                        0
                                    )
                                )
                            )
                        ),
                        5
                    ), 
                    if("hdom">15,
                        -1, 
                        if("hdom">9,
                            -2,
                            -3
                        )
                    )
                ),
                if("hdom">=18, 
                    if("DG_os" + "DG_ueb" >= 45, 
                        if("DG_ms" >= 35,
                            4,
                            if("DG_ms">=25,
                                if("DG_us" + "DG_ks">=20,
                                    3,
                                    2
                                ),
                                if("DG_ms">=15,
                                    if("DG_us"+ "DG_ks">=10,
                                        2,
                                        1
                                    ),
                                    if("DG_us"+"DG_ks">=10,
                                        1,
                                        0
                                    )
                                )
                            )
                        ),
                    5), 
                    if("hdom">13,
                        -1, 
                        if("hdom">8,
                            -2,
                            -3
                        )
                    )
                )
            ),
            if("NH">50,
                if("hdom">=18, 
                    if("DG_os" + "DG_ueb" >= 45, 
                        if("DG_ms" >= 35,
                        4,
                            if("DG_ms">=25,
                                if("DG_us" + "DG_ks">=20,
                                    3,
                                    2
                                ),
                                if("DG_ms">=15,
                                    if("DG_us"+ "DG_ks">=10,
                                        2,
                                        1
                                    ),
                                    if("DG_us"+"DG_ks">=10,
                                        1,
                                        0
                                    )
                                )
                            )
                        ),
                        5
                    ), 
                    if("hdom">13,
                        -1, 
                        if("hdom">8,
                            -2,
                            -3
                        )
                    )
                ),
                if("hdom">=15, 
                    if("DG_os" + "DG_ueb" >= 45, 
                        if("DG_ms" >= 35,
                            4,
                            if("DG_ms">=25,
                                if("DG_us" + "DG_ks">=20,
                                    3,
                                    2
                                ),
                                if("DG_ms">=15,
                                    if("DG_us"+ "DG_ks">=10,
                                        2,
                                        1
                                    ),
                                    if("DG_us"+"DG_ks">=10,
                                        1,
                                        0
                                    )
                                )
                            )
                        ),
                    5), 
                    if("hdom">10,
                        -1, 
                        if("hdom">7,
                            -2,
                            -3
                        )
                    )
                )
            )
        )
    )
)) + 

')' + 

to_string(if("DG_os" + "DG_ueb" < 35, 5, if("DG_os" + "DG_ueb" <45, 4, if("DG_os" + "DG_ueb" <= 55, 3, if("DG_os" + "DG_ueb" < 70, 2, if("DG_os" + "DG_ueb" < 85, 1, 0)))))) + 

to_string(if("DG_ms" > 45, 5, if("DG_ms" > 35, 4, if("DG_ms" >= 25, 3, if("DG_ms" >= 15, 2, if("DG_ms" >= 5, 1, 0)))))) + 

to_string(if("DG_us" + "DG_ks" > 40, 5, if("DG_us" + "DG_ks" > 30, 4, if("DG_us" + "DG_ks" >= 20, 3, if("DG_us" + "DG_ks" >= 10, 2, if("DG_us" + "DG_ks" > 1, 1, 0))))))
 
+ '\n' + 
to_string("DG_os" + "DG_ueb") + '.' + 
to_string("DG_ms") + '.' + 
to_string("DG_us"+ "DG_ks")




###  ----------------------  ###
def -#--- v4 Dauerwald Labels VegZone mit KS 2023-12-20:
###  ----------------------  ###
    VegZone.hdom.NH
    Phase_Offiziell [GL* 10 / 20 / 35 / 55 / 75] (Ph_os Ph_ms Ph_us)
    DG_os.DG_ms.DG_us.DG_ks


-- Vegetationshöhenstufe
if("VegZone_Code" IN (2), 
    'KL',
    if("VegZone_Code" IN (4),
        'SM',
        if("VegZone_Code" IN (5),
            'UM',
            if("VegZone_Code" IN (6, 7),
                'OM',
                if("VegZone_Code" IN (8),
                    'HM',
                     if("VegZone_Code" IN (9),
                    'SA',
                    '??'
                    )
                )
            )
        )    
    )
) 
-- hdom.NH
+ to_string("hdom") + '.' 
+ to_string(to_int(round(to_real("NH")/10))) + 

'\n' + 

-- Dauerwaldphase
to_string(
if("VegZone_Code" IN (-1, 0, 1, 2, 4, 5), 
    if("NH">50,
        if("hdom">=26, 
            if("DG_os" + "DG_ueb" >= 45, 
                if("DG_ms" >= 35,
                4,
                    if("DG_ms">=25,
                        if("DG_us" >=20,
                            3,
                            2
                        ),
                        if("DG_ms">=15,
                            if("DG_us">=10,
                                2,
                                1
                            ),
                            if("DG_us">=10,
                                1,
                                0
                            )
                        )
                    )
                ),
                5
            ), 
            if("hdom">18,
                -1, 
                if("hdom">10,
                    -2,
                    -3
                )
            )
        ),
        if("hdom">=23, 
            if("DG_os" + "DG_ueb" >= 45, 
                if("DG_ms" >= 35,
                    4,
                    if("DG_ms">=25,
                        if("DG_us" >=20,
                            3,
                            2
                        ),
                        if("DG_ms">=15,
                            if("DG_us">=10,
                                2,
                                1
                            ),
                            if("DG_us">=10,
                                1,
                                0
                            )
                        )
                    )
                ),
            5), 
            if("hdom">16,
                -1, 
                if("hdom">9,
                    -2,
                    -3
                )
            )
        )
    ),
    if ("VegZone_Code" IN (6, 7),
        if("NH">50,
            if("hdom">=23, 
                if("DG_os" + "DG_ueb" >= 45, 
                    if("DG_ms" >= 35,
                    4,
                        if("DG_ms">=25,
                            if("DG_us" >=20,
                                3,
                                2
                            ),
                            if("DG_ms">=15,
                                if("DG_us">=10,
                                    2,
                                    1
                                ),
                                if("DG_us">=10,
                                    1,
                                    0
                                )
                            )
                        )
                    ),
                    5
                ), 
                if("hdom">16,
                    -1, 
                    if("hdom">9,
                        -2,
                        -3
                    )
                )
            ),
            if("hdom">=19, 
                if("DG_os" + "DG_ueb" >= 45, 
                    if("DG_ms" >= 35,
                        4,
                        if("DG_ms">=25,
                            if("DG_us" >=20,
                                3,
                                2
                            ),
                            if("DG_ms">=15,
                                if("DG_us">=10,
                                    2,
                                    1
                                ),
                                if("DG_us">=10,
                                    1,
                                    0
                                )
                            )
                        )
                    ),
                5), 
                if("hdom">13,
                    -1, 
                    if("hdom">7,
                        -2,
                        -3
                    )
                )
            )
        ),
        if("VegZone_Code" IN (8),
            if("NH">50,
                if("hdom">=19, 
                    if("DG_os" + "DG_ueb" >= 45, 
                        if("DG_ms" >= 35,
                        4,
                            if("DG_ms">=25,
                                if("DG_us" >=20,
                                    3,
                                    2
                                ),
                                if("DG_ms">=15,
                                    if("DG_us">=10,
                                        2,
                                        1
                                    ),
                                    if("DG_us">=10,
                                        1,
                                        0
                                    )
                                )
                            )
                        ),
                        5
                    ), 
                    if("hdom">13,
                        -1, 
                        if("hdom">7,
                            -2,
                            -3
                        )
                    )
                ),
                if("hdom">=16, 
                    if("DG_os" + "DG_ueb" >= 45, 
                        if("DG_ms" >= 35,
                            4,
                            if("DG_ms">=25,
                                if("DG_us" >=20,
                                    3,
                                    2
                                ),
                                if("DG_ms">=15,
                                    if("DG_us">=10,
                                        2,
                                        1
                                    ),
                                    if("DG_us">=10,
                                        1,
                                        0
                                    )
                                )
                            )
                        ),
                    5), 
                    if("hdom">11,
                        -1, 
                        if("hdom">6,
                            -2,
                            -3
                        )
                    )
                )
            ),
            if("NH">50,
                if("hdom">=16, 
                    if("DG_os" + "DG_ueb" >= 45, 
                        if("DG_ms" >= 35,
                        4,
                            if("DG_ms">=25,
                                if("DG_us" >=20,
                                    3,
                                    2
                                ),
                                if("DG_ms">=15,
                                    if("DG_us">=10,
                                        2,
                                        1
                                    ),
                                    if("DG_us">=10,
                                        1,
                                        0
                                    )
                                )
                            )
                        ),
                        5
                    ), 
                    if("hdom">11,
                        -1, 
                        if("hdom">6,
                            -2,
                            -3
                        )
                    )
                ),
                if("hdom">=13, 
                    if("DG_os" + "DG_ueb" >= 45, 
                        if("DG_ms" >= 35,
                            4,
                            if("DG_ms">=25,
                                if("DG_us" >=20,
                                    3,
                                    2
                                ),
                                if("DG_ms">=15,
                                    if("DG_us">=10,
                                        2,
                                        1
                                    ),
                                    if("DG_us">=10,
                                        1,
                                        0
                                    )
                                )
                            )
                        ),
                    5), 
                    if("hdom">9,
                        -1, 
                        if("hdom">5,
                            -2,
                            -3
                        )
                    )
                )
            )
        )
    )
)
) 
 
+
-- Dauerwaldphase Zusatz * bei hohem Anteil Keine Schicht
if("DG_ks" > 10, '*','')  + 
if("DG_ks" > 20, '*','')  + 
if("DG_ks" > 35, '*','')  + 
if("DG_ks" > 55, '*','')  + 
if("DG_ks" > 75, '*','')  + 

'(' + 

-- Dauerwaldphase pro Schicht/Stufe
to_string(if("DG_os" + "DG_ueb" < 35, 5, if("DG_os" + "DG_ueb" <45, 4, if("DG_os" + "DG_ueb" <= 55, 3, if("DG_os" + "DG_ueb" < 70, 2, if("DG_os" + "DG_ueb" < 85, 1, 0)))))) + 

to_string(if("DG_ms" > 45, 5, if("DG_ms" > 35, 4, if("DG_ms" >= 25, 3, if("DG_ms" >= 15, 2, if("DG_ms" >= 5, 1, 0)))))) + 

to_string(if("DG_us" > 40, 5, if("DG_us" > 30, 4, if("DG_us" >= 20, 3, if("DG_us" >= 10, 2, if("DG_us" > 1, 1, 0))))))

')' + 
 
'\n' 

+ 
-- Deckungsgrad pro Schicht/Stufe
to_string("DG_os" + "DG_ueb") + '.' + 
to_string("DG_ms") + '.' + 
to_string("DG_us") + '.' + 
to_string("DG_ks")




###  ----------------------  ###
def -#--- v5 Dauerwald Labels VegZone mit a/b/c Zusatz:
###  ----------------------  ###

-- Diese Expression baut das folgende Label:
--    VegZone.hdom.NH
--    Phase_Offiziell [a/b/c] [GL* 10 / 20 / 35 / 55 / 75] (Ph_os Ph_ms Ph_us)
--    DG_os.DG_ms.DG_us.DG_ks


-- Vegetationshöhenstufe.hdom.NH
if("VegZone_Code" IN (2), 
    'KL',
    if("VegZone_Code" IN (4),
        'SM',
        if("VegZone_Code" IN (5),
            'UM',
            if("VegZone_Code" IN (6, 7),
                'OM',
                if("VegZone_Code" IN (8),
                    'HM',
                     if("VegZone_Code" IN (9),
                    'SA',
                    '??'
                    )
                )
            )
        )    
    )
) + '.' + 
to_string("hdom") + '.' + 
to_string(to_int(round(to_real("NH")/10))) + 

'\n' + 

-- Dauerwaldphase
with_variable(
'DW_Code',
-- Berechnung DW_Code
if("VegZone_Code" IN (-1, 0, 1, 2, 4, 5),
    -- Case: Default (KL/SM/UM + andere)
    if("NH">50,
        -- KL/SM/UM, NH
        if("hdom">=26, 
            if("DG_os" + "DG_ueb" >= 45, 
                if("DG_ms" >= 35,
                4,
                    if("DG_ms">=25,
                        if("DG_us" >=20,
                            3,
                            2
                        ),
                        if("DG_ms">=15,
                            if("DG_us">=10,
                                2,
                                1
                            ),
                            if("DG_us">=10,
                                1,
                                0
                            )
                        )
                    )
                ),
                5
            ), 
            -- KL/SM/UM, NH, Jungwald
            if("hdom">18,
                -1, 
                if("hdom">10,
                    -2,
                    -3
                )
            )
        ),
        -- KL/SM/UM, LH
        if("hdom">=23, 
            if("DG_os" + "DG_ueb" >= 45, 
                if("DG_ms" >= 35,
                    4,
                    if("DG_ms">=25,
                        if("DG_us" >=20,
                            3,
                            2
                        ),
                        if("DG_ms">=15,
                            if("DG_us">=10,
                                2,
                                1
                            ),
                            if("DG_us">=10,
                                1,
                                0
                            )
                        )
                    )
                ),
            5), 
            -- KL/SM/UM, LH, Jungwald
            if("hdom">16,
                -1, 
                if("hdom">9,
                    -2,
                    -3
                )
            )
        )
    ),
    -- Case: Obermontan (OM)
    if ("VegZone_Code" IN (6, 7),
        if("NH">50,
            -- OM, NH
            if("hdom">=23, 
                if("DG_os" + "DG_ueb" >= 45, 
                    if("DG_ms" >= 35,
                    4,
                        if("DG_ms">=25,
                            if("DG_us" >=20,
                                3,
                                2
                            ),
                            if("DG_ms">=15,
                                if("DG_us">=10,
                                    2,
                                    1
                                ),
                                if("DG_us">=10,
                                    1,
                                    0
                                )
                            )
                        )
                    ),
                    5
                ), 
                -- OM, NH, Jungwald
                if("hdom">16,
                    -1, 
                    if("hdom">9,
                        -2,
                        -3
                    )
                )
            ),
            -- OM, LH
            if("hdom">=19, 
                if("DG_os" + "DG_ueb" >= 45, 
                    if("DG_ms" >= 35,
                        4,
                        if("DG_ms">=25,
                            if("DG_us" >=20,
                                3,
                                2
                            ),
                            if("DG_ms">=15,
                                if("DG_us">=10,
                                    2,
                                    1
                                ),
                                if("DG_us">=10,
                                    1,
                                    0
                                )
                            )
                        )
                    ),
                5), 
                -- OM, LH, Jungwald
                if("hdom">13,
                    -1, 
                    if("hdom">7,
                        -2,
                        -3
                    )
                )
            )
        ),
        -- Case Hochmontan (HM)
        if("VegZone_Code" IN (8),
            if("NH">50,
                -- HM, NH
                if("hdom">=19, 
                    if("DG_os" + "DG_ueb" >= 45, 
                        if("DG_ms" >= 35,
                        4,
                            if("DG_ms">=25,
                                if("DG_us" >=20,
                                    3,
                                    2
                                ),
                                if("DG_ms">=15,
                                    if("DG_us">=10,
                                        2,
                                        1
                                    ),
                                    if("DG_us">=10,
                                        1,
                                        0
                                    )
                                )
                            )
                        ),
                        5
                    ), 
                    -- HM, NH, Jungwald
                    if("hdom">13,
                        -1, 
                        if("hdom">7,
                            -2,
                            -3
                        )
                    )
                ),
                -- HM, LH
                if("hdom">=16, 
                    if("DG_os" + "DG_ueb" >= 45, 
                        if("DG_ms" >= 35,
                            4,
                            if("DG_ms">=25,
                                if("DG_us" >=20,
                                    3,
                                    2
                                ),
                                if("DG_ms">=15,
                                    if("DG_us">=10,
                                        2,
                                        1
                                    ),
                                    if("DG_us">=10,
                                        1,
                                        0
                                    )
                                )
                            )
                        ),
                    5), 
                    -- HM, LH, Jungwald
                    if("hdom">11,
                        -1, 
                        if("hdom">6,
                            -2,
                            -3
                        )
                    )
                )
            ),
            -- Case Subalpin (SA)
            if("NH">50,
                -- SA, NH
                if("hdom">=16, 
                    if("DG_os" + "DG_ueb" >= 45, 
                        if("DG_ms" >= 35,
                        4,
                            if("DG_ms">=25,
                                if("DG_us" >=20,
                                    3,
                                    2
                                ),
                                if("DG_ms">=15,
                                    if("DG_us">=10,
                                        2,
                                        1
                                    ),
                                    if("DG_us">=10,
                                        1,
                                        0
                                    )
                                )
                            )
                        ),
                        5
                    ), 
                    -- SA, NH, Jungwald
                    if("hdom">11,
                        -1, 
                        if("hdom">6,
                            -2,
                            -3
                        )
                    )
                ),
                -- SA, LH
                if("hdom">=13, 
                    if("DG_os" + "DG_ueb" >= 45, 
                        if("DG_ms" >= 35,
                            4,
                            if("DG_ms">=25,
                                if("DG_us" >=20,
                                    3,
                                    2
                                ),
                                if("DG_ms">=15,
                                    if("DG_us">=10,
                                        2,
                                        1
                                    ),
                                    if("DG_us">=10,
                                        1,
                                        0
                                    )
                                )
                            )
                        ),
                    5), 
                    -- SA, LH, Jungwald
                    if("hdom">9,
                        -1, 
                        if("hdom">5,
                            -2,
                            -3
                        )
                    ) -- close Jungwaldphase if
                ) -- close Jungwald/Altwald if
            ) -- close NH/LH if
        ) -- close HM/SA if
    ) -- close OM/other if
) -- close (KL/SM/UM/...)/other if
, -- Start: Expression with variable @DW_Code
-- Add DW_Code
to_string(@DW_Code) +

if(@DW_Code IN (1,2,3), 
if("VegZone_Code" IN (-1, 0, 1, 2, 4, 5),
    -- Case: Default (KL/SM/UM + andere)
    if("NH">50,
        -- KL/SM/UM, NH
        if("hdom">=38, 'c',
            if("hdom" >= 33, 'b', 'a')
        ),
        -- KL/SM/UM, LH
        if("hdom">=33, 'c',
            if("hdom" >= 29, 'b', 'a')
        )
    ),
    -- Case: Obermontan (OM)
    if ("VegZone_Code" IN (6, 7),
        if("NH">50,
            -- OM, NH
            if("hdom">=33, 'c',
                if("hdom" >= 29, 'b', 'a')
            ),
            -- OM, LH
            if("hdom">=23, 'c',
                if("hdom" >= 29, 'b', 'a')
            )
        ),
        -- Case Hochmontan (HM)
        if("VegZone_Code" IN (8),
            if("NH">50,
                -- HM, NH
                if("hdom">=23, 'c',
                    if("hdom" >= 29, 'b', 'a')
                ),
                -- HM, LH
                if("hdom">=19, 'c',
                    if("hdom" >= 23, 'b', 'a')
                )
            ),
            -- Case Subalpin (SA)
            if("NH">50,
                -- SA, NH
                if("hdom">=19, 'c',
                    if("hdom" >= 23, 'b', 'a')
                ),
                -- SA, LH
                if("hdom">=16, 'c',
                    if("hdom" >= 19, 'b', 'a')
                ) -- close a/b/c if
            ) -- close NH/LH if
        ) -- close HM/SA if
    ) -- close OM/other if
) -- close (KL/SM/UM/...)/other if
, '' -- else add no abc
) -- close structure/no no abc if 
) -- close expression with @DW_Code

+
-- Dauerwaldphase Zusatz * bei hohem Anteil Keine Schicht
if("DG_ks" > 10, '*','')  + 
if("DG_ks" > 20, '*','')  + 
if("DG_ks" > 35, '*','')  + 
if("DG_ks" > 55, '*','')  + 
if("DG_ks" > 75, '*','')  + 


-- Dauerwaldphase pro Schicht/Stufe
'(' + 

to_string(if("DG_os" + "DG_ueb" < 35, 5, if("DG_os" + "DG_ueb" <45, 4, if("DG_os" + "DG_ueb" <= 55, 3, if("DG_os" + "DG_ueb" < 70, 2, if("DG_os" + "DG_ueb" < 85, 1, 0)))))) + 

to_string(if("DG_ms" > 45, 5, if("DG_ms" > 35, 4, if("DG_ms" >= 25, 3, if("DG_ms" >= 15, 2, if("DG_ms" >= 5, 1, 0)))))) + 

to_string(if("DG_us" > 40, 5, if("DG_us" > 30, 4, if("DG_us" >= 20, 3, if("DG_us" >= 10, 2, if("DG_us" > 1, 1, 0)))))) +

')' + 
 
'\n' + 
-- Deckungsgrad pro Schicht/Stufe
to_string("DG_os" + "DG_ueb") + '.' + 
to_string("DG_ms") + '.' + 
to_string("DG_us") + '.' + 
to_string("DG_ks")



###  ----------------------  ###
def --#--- CALC DW_CODE a/b/c -----:
###  ----------------------  ###
# these calculations provide the logic to determine whether category a/b/c are applied (only on DW_Code 1-3)
# which can then be used to apply a symbology
# on some cases we want no symbology, e.g. a && DW_Code=1, b && DW_Code=2, c && DW_Code=3
with_variable(
'DW_Code',
-- Berechnung DW_Code
if("VegZone_Code" IN (-1, 0, 1, 2, 4, 5),
    -- Case: Default (KL/SM/UM + andere)
    if("NH">50,
        -- KL/SM/UM, NH
        if("hdom">=26, 
            if("DG_os" + "DG_ueb" >= 45, 
                if("DG_ms" >= 35,
                4,
                    if("DG_ms">=25,
                        if("DG_us" >=20,
                            3,
                            2
                        ),
                        if("DG_ms">=15,
                            if("DG_us">=10,
                                2,
                                1
                            ),
                            if("DG_us">=10,
                                1,
                                0
                            )
                        )
                    )
                ),
                5
            ), 
            -- KL/SM/UM, NH, Jungwald
            if("hdom">18,
                -1, 
                if("hdom">10,
                    -2,
                    -3
                )
            )
        ),
        -- KL/SM/UM, LH
        if("hdom">=23, 
            if("DG_os" + "DG_ueb" >= 45, 
                if("DG_ms" >= 35,
                    4,
                    if("DG_ms">=25,
                        if("DG_us" >=20,
                            3,
                            2
                        ),
                        if("DG_ms">=15,
                            if("DG_us">=10,
                                2,
                                1
                            ),
                            if("DG_us">=10,
                                1,
                                0
                            )
                        )
                    )
                ),
            5), 
            -- KL/SM/UM, LH, Jungwald
            if("hdom">16,
                -1, 
                if("hdom">9,
                    -2,
                    -3
                )
            )
        )
    ),
    -- Case: Obermontan (OM)
    if ("VegZone_Code" IN (6, 7),
        if("NH">50,
            -- OM, NH
            if("hdom">=23, 
                if("DG_os" + "DG_ueb" >= 45, 
                    if("DG_ms" >= 35,
                    4,
                        if("DG_ms">=25,
                            if("DG_us" >=20,
                                3,
                                2
                            ),
                            if("DG_ms">=15,
                                if("DG_us">=10,
                                    2,
                                    1
                                ),
                                if("DG_us">=10,
                                    1,
                                    0
                                )
                            )
                        )
                    ),
                    5
                ), 
                -- OM, NH, Jungwald
                if("hdom">16,
                    -1, 
                    if("hdom">9,
                        -2,
                        -3
                    )
                )
            ),
            -- OM, LH
            if("hdom">=19, 
                if("DG_os" + "DG_ueb" >= 45, 
                    if("DG_ms" >= 35,
                        4,
                        if("DG_ms">=25,
                            if("DG_us" >=20,
                                3,
                                2
                            ),
                            if("DG_ms">=15,
                                if("DG_us">=10,
                                    2,
                                    1
                                ),
                                if("DG_us">=10,
                                    1,
                                    0
                                )
                            )
                        )
                    ),
                5), 
                -- OM, LH, Jungwald
                if("hdom">13,
                    -1, 
                    if("hdom">7,
                        -2,
                        -3
                    )
                )
            )
        ),
        -- Case Hochmontan (HM)
        if("VegZone_Code" IN (8),
            if("NH">50,
                -- HM, NH
                if("hdom">=19, 
                    if("DG_os" + "DG_ueb" >= 45, 
                        if("DG_ms" >= 35,
                        4,
                            if("DG_ms">=25,
                                if("DG_us" >=20,
                                    3,
                                    2
                                ),
                                if("DG_ms">=15,
                                    if("DG_us">=10,
                                        2,
                                        1
                                    ),
                                    if("DG_us">=10,
                                        1,
                                        0
                                    )
                                )
                            )
                        ),
                        5
                    ), 
                    -- HM, NH, Jungwald
                    if("hdom">13,
                        -1, 
                        if("hdom">7,
                            -2,
                            -3
                        )
                    )
                ),
                -- HM, LH
                if("hdom">=16, 
                    if("DG_os" + "DG_ueb" >= 45, 
                        if("DG_ms" >= 35,
                            4,
                            if("DG_ms">=25,
                                if("DG_us" >=20,
                                    3,
                                    2
                                ),
                                if("DG_ms">=15,
                                    if("DG_us">=10,
                                        2,
                                        1
                                    ),
                                    if("DG_us">=10,
                                        1,
                                        0
                                    )
                                )
                            )
                        ),
                    5), 
                    -- HM, LH, Jungwald
                    if("hdom">11,
                        -1, 
                        if("hdom">6,
                            -2,
                            -3
                        )
                    )
                )
            ),
            -- Case Subalpin (SA)
            if("NH">50,
                -- SA, NH
                if("hdom">=16, 
                    if("DG_os" + "DG_ueb" >= 45, 
                        if("DG_ms" >= 35,
                        4,
                            if("DG_ms">=25,
                                if("DG_us" >=20,
                                    3,
                                    2
                                ),
                                if("DG_ms">=15,
                                    if("DG_us">=10,
                                        2,
                                        1
                                    ),
                                    if("DG_us">=10,
                                        1,
                                        0
                                    )
                                )
                            )
                        ),
                        5
                    ), 
                    -- SA, NH, Jungwald
                    if("hdom">11,
                        -1, 
                        if("hdom">6,
                            -2,
                            -3
                        )
                    )
                ),
                -- SA, LH
                if("hdom">=13, 
                    if("DG_os" + "DG_ueb" >= 45, 
                        if("DG_ms" >= 35,
                            4,
                            if("DG_ms">=25,
                                if("DG_us" >=20,
                                    3,
                                    2
                                ),
                                if("DG_ms">=15,
                                    if("DG_us">=10,
                                        2,
                                        1
                                    ),
                                    if("DG_us">=10,
                                        1,
                                        0
                                    )
                                )
                            )
                        ),
                    5), 
                    -- SA, LH, Jungwald
                    if("hdom">9,
                        -1, 
                        if("hdom">5,
                            -2,
                            -3
                        )
                    ) -- close Jungwaldphase if
                ) -- close Jungwald/Altwald if
            ) -- close NH/LH if
        ) -- close HM/SA if
    ) -- close OM/other if
) -- close (KL/SM/UM/...)/other if

, -- Start: Expression with variable @DW_Code

with_variable('DW_Code_abc',
-- Berechnung DW_Code_abc
if(@DW_Code IN (0,1,2,3,4,5), 
if("VegZone_Code" IN (-1, 0, 1, 2, 4, 5),
    -- Case: Default (KL/SM/UM + andere)
    if("NH">50,
        -- KL/SM/UM, NH
        if("hdom">=38, 'c',
            if("hdom" >= 33, 'b', 'a')
        ),
        -- KL/SM/UM, LH
        if("hdom">=33, 'c',
            if("hdom" >= 29, 'b', 'a')
        )
    ),
    -- Case: Obermontan (OM)
    if ("VegZone_Code" IN (6, 7),
        if("NH">50,
            -- OM, NH
            if("hdom">=33, 'c',
                if("hdom" >= 29, 'b', 'a')
            ),
            -- OM, LH
            if("hdom">=23, 'c',
                if("hdom" >= 29, 'b', 'a')
            )
        ),
        -- Case Hochmontan (HM)
        if("VegZone_Code" IN (8),
            if("NH">50,
                -- HM, NH
                if("hdom">=23, 'c',
                    if("hdom" >= 29, 'b', 'a')
                ),
                -- HM, LH
                if("hdom">=19, 'c',
                    if("hdom" >= 23, 'b', 'a')
                )
            ),
            -- Case Subalpin (SA)
            if("NH">50,
                -- SA, NH
                if("hdom">=19, 'c',
                    if("hdom" >= 23, 'b', 'a')
                ),
                -- SA, LH
                if("hdom">=16, 'c',
                    if("hdom" >= 19, 'b', 'a')
                ) -- close a/b/c if
            ) -- close NH/LH if
        ) -- close HM/SA if
    ) -- close OM/other if
) -- close (KL/SM/UM/...)/other if
, '' -- else add no abc
) -- close structure/no no abc if

, -- Start: Expression with variable @DW_Code_abc
-- check if symbology is needed (on some cases we want no symbology, e.g. a && DW_Code=1, b && DW_Code=2, c && DW_Code=3)
if( (@DW_Code_abc = 'a' AND @DW_Code = 1) OR (@DW_Code_abc = 'b' AND @DW_Code = 2) OR (@DW_Code_abc = 'c' AND @DW_Code = 3), '', @DW_Code_abc) 
) -- close: Expression with variable @DW_Code_abc
) -- close expression with @DW_Code