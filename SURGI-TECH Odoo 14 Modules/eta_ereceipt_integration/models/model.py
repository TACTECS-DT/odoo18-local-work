# -*- coding: utf-8 -*-

##############################################################################
#
#
#    Copyright (C) 2019-TODAY .
#    Author: Plementus <https://plementus.com>
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import json
import hashlib

receipt = {
    "header": {
        "dateTimeIssued": "2022-06-12T00:00:00Z",
        "receiptNumber": "2000000087",
        "uuid": "",
        "previousUUID": "",
        "referenceOldUUID": "",
        "currency": "EGP",
        "exchangeRate": 0,
        "sOrderNameCode": "sOrderNameCode",
        "orderdeliveryMode": "",
        "grossWeight": 6.43,
        "netWeight": 6.89
    },
    "documentType": {
        "receiptType": "S",
        "typeVersion": "1.0"
    },
    "seller": {
        "rin": "508695732",
        "companyTradeName": "Oppo Egypt",
        "branchCode": "0",
        "branchAddress": {
            "country": "EG",
            "governate": "cairo",
            "regionCity": "nasr city",
            "street": "22 makrm abed st",
            "buildingNumber": "18",
            "postalCode": "74235",
            "floor": "1",
            "room": "3",
            "landmark": "",
            "additionalInformation": ""
        },
        "deviceSerialNumber": "159753",
        "syndicateLicenseNumber": "",
        "activityCode": "4759"
    },
    "buyer": {
        "type": "B",
        "id": "113317713",
        "name": "Taxpayer1",
        "mobileNumber": "01020567462",
        "paymentNumber": "987654"
    },
    "itemData": [
        {
            "internalCode": "8806092129306",
            "description": "Oppo Reno6 5G",
            "itemType": "GS1",
            "itemCode": "10003779",
            "unitType": "EA",
            "quantity": 7.0,
            "unitPrice": 13.5,
            "netSale": 92.988,
            "totalSale": 94.5,
            "total": 96.95192,
            "commercialDiscount": [
                0.512,
                1.0
            ],
            "itemDiscount": [
                2.8,
                1.1
            ],
            "valueDifference": -5.0,
            "taxableItems": [
                {
                    "taxType": "T1",
                    "subType": "V001",
                    "amount": 12.31832,
                    "rate": 14.0
                },
                {
                    "taxType": "T4",
                    "subType": "W001",
                    "amount": 4.4544,
                    "rate": 5.0
                }
            ]
        },
        {
            "internalCode": "10000019",
            "description": "Oppo A55",
            "itemType": "GS1",
            "itemCode": "10003779",
            "unitType": "EA",
            "quantity": 89,
            "unitPrice": 150.987,
            "netSale": 13303.46457,
            "totalSale": 13437.843,
            "total": 14762.15667,
            "commercialDiscount": [
                34.37843,
                100.0
            ],
            "itemDiscount": [
                2.0,
                3.7
            ],
            "valueDifference": 6.0,
            "taxableItems": [
                {
                    "taxType": "T1",
                    "subType": "V009",
                    "amount": 1863.32504,
                    "rate": 14.0
                },
                {
                    "taxType": "T4",
                    "subType": "W001",
                    "amount": 398.93294,
                    "rate": 3.0
                }
            ]
        }
    ],
    "totalSales": 13532.343,
    "totalCommercialDiscount": 135.89043,
    "totalItemsDiscount": 9.6,
    "extraReceiptDiscount": [
        25.49
    ],
    "netAmount": 13396.45257,
    "feesAmount": 10.065,
    "totalAmount": 14808.12859,
    "taxTotals": [
        {
            "taxType": "T1",
            "amount": 1875.64336
        },
        {
            "taxType": "T4",
            "amount": 403.38734
        }
    ],
    "paymentMethod": "Cash",
    "adjustment": 3.789,
    "contractor": {
        "name": "contractor1",
        "amount": 2.563,
        "rate": 2.3
    },
    "beneficiary": {
        "amount": 20.569,
        "rate": 2.147
    }
}

receipt = {
    "header": {
        "dateTimeIssued": "2022-09-14T00:00:00Z",
        "receiptNumber": "1234566",
        "uuid": "",
        "previousUUID": "",
        "referenceOldUUID": "",
        "currency": "EGP",
        "exchangeRate": 0,
        "sOrderNameCode": "sOrderNameCode",
        "orderdeliveryMode": "AIR",
        "grossWeight": 6.43,
        "netWeight": 6.89
    },
    "documentType": {
        "receiptType": "S",
        "typeVersion": "1.0"
    },
    "seller": {
        "rin": "100290787",
        "companyTradeName": "شركة مزرعة سامي جرجس",
        "branchCode": "0",
        "branchAddress": {
            "country": "EG",
            "governate": "cairo",
            "regionCity": "Zamalek",
            "street": "14 street",
            "buildingNumber": "18",
            "postalCode": "74235",
            "floor": "1",
            "room": "3",
            "landmark": "",
            "additionalInformation": ""
        },
        "deviceSerialNumber": "159755",
        "syndicateLicenseNumber": "",
        "activityCode": "4649"
    },
    "buyer": {
        "type": "B",
        "id": "113317713",
        "name": "Taxpayer1",
        "mobileNumber": "+201020567462",
        "paymentNumber": "987654"
    },
    "itemData": [
        {
            "internalCode": "99999999",
            "description": "Test Product",
            "itemType": "GS1",
            "itemCode": "99999999",
            "unitType": "EA",
            "quantity": 7.0,
            "unitPrice": 13.5,
            "netSale": 92.988,
            "totalSale": 94.5,
            "total": 96.95192,
            "commercialDiscount": [
                0.512,
                1.0
            ],
            "itemDiscount": [
                2.8,
                1.1
            ],
            "valueDifference": -5.0,
            "taxableItems": [
                {
                    "taxType": "T1",
                    "subType": "V001",
                    "amount": 12.31832,
                    "rate": 14.0
                },
                {
                    "taxType": "T4",
                    "subType": "W001",
                    "amount": 4.4544,
                    "rate": 5.0
                }
            ]
        },
        {
            "internalCode": "10000019",
            "description": "Oppo A55",
            "itemType": "GS1",
            "itemCode": "10003779",
            "unitType": "EA",
            "quantity": 89,
            "unitPrice": 150.987,
            "netSale": 13303.46457,
            "totalSale": 13437.843,
            "total": 14762.15667,
            "commercialDiscount": [
                34.37843,
                100.0
            ],
            "itemDiscount": [
                2.0,
                3.7
            ],
            "valueDifference": 6.0,
            "taxableItems": [
                {
                    "taxType": "T1",
                    "subType": "V009",
                    "amount": 1863.32504,
                    "rate": 14.0
                },
                {
                    "taxType": "T4",
                    "subType": "W001",
                    "amount": 398.93294,
                    "rate": 3.0
                }
            ]
        }
    ],
    "totalSales": 13532.343,
    "totalCommercialDiscount": 135.89043,
    "totalItemsDiscount": 9.6,
    "extraReceiptDiscount": [
        25.49
    ],
    "netAmount": 13396.45257,
    "feesAmount": 10.065,
    "totalAmount": 14808.12859,
    "taxTotals": [
        {
            "taxType": "T1",
            "amount": 1875.64336
        },
        {
            "taxType": "T4",
            "amount": 403.38734
        }
    ],
    "paymentMethod": "Cash",
    "adjustment": 3.789,
    "contractor": {
        "name": "contractor1",
        "amount": 2.563,
        "rate": 2.3
    },
    "beneficiary": {
        "amount": 20.569,
        "rate": 2.147
    }
}


# receipt2 = {
#             "header": {
#                  "dateTimeIssued": "2022-06-07T00:00:00Z",
#                 "receiptNumber": "1234566",
#                 "uuid":"",
#                 "previousUUID": "b4c08c8b273c45d6b824b359d87d957345b0ec6859eb4ad7b68221244ca55d86",
#                 "referenceOldUUID": "",
#                 "currency": "EGP",
#                 "exchangeRate": 0,
#                 "sOrderNameCode": "sOrderNameCode",
#                 "orderdeliveryMode": "AIR",
#                 "grossWeight": 6.43,
#                 "netWeight": 6.89
#             },
#             "documentType": {
#                 "receiptType": "S",
#                 "typeVersion": "1.0"
#             },
#             "seller": {
#                 "rin": "410742090",
#                 "companyTradeName": "Asmak Ba7ry",
#                 "branchCode": "0",
#                 "branchAddress": {
#                     "country": "EG",
#                     "governate": "cairo",
#                     "regionCity": "city center",
#                     "street": "14 street",
#                     "buildingNumber": "18",
#                     "postalCode": "74235",
#                     "floor": "1",
#                     "room": "3",
#                     "landmark": "tahrir square",
#                     "additionalInformation": "talaat harb street"
#                 },
#                 "deviceSerialNumber": "YV200T573",
#                 "syndicateLicenseNumber": "1000056",
#                 "activityCode": "4620"
#             },
#             "buyer": {
#                 "type": "B",
#                 "id": "113317713",
#                 "name": "Taxpayer1",
#                 "mobileNumber": "+201020567462",
#                 "paymentNumber": "987654"
#             },
#             "itemData": [
#                 {
#                     "internalCode": "8806092129306",
#                     "description": "Samsung A02 32GB_LTE_BLACK_DS_SM-A022FZKDMEB_A022 _ A022_SM-A022FZKDMEB",
#                     "itemType": "GS1",
#                     "itemCode": "10007020",
#                     "unitType": "EA",
#                     "quantity": 7.0,
#                     "unitPrice": 13.5,
#                     "netSale": 92.988,
#                     "totalSale": 94.50,
#                     "total": 96.95192,
#                     "commercialDiscount": [
#                         0.512,
#                         1.00
#                     ],
#                     "itemDiscount": [
#                         2.8,
#                         1.1
#                     ],
#                     "valueDifference": -5.0,
#                     "taxableItems": [
#                         {
#                             "taxType": "T1",
#                             "subType": "V001",
#                             "amount": 12.31832,
#                             "rate": 14.0
#                         },
#                         {
#                             "taxType": "T4",
#                             "subType": "W001",
#                             "amount": 4.4544,
#                             "rate": 5.0
#                         }
#                     ]
#                 },
#                 {
#                     "internalCode": "10000019",
#                     "description": "Petcare",
#                     "itemType": "GS1",
#                     "itemCode": "058496022761",
#                     "unitType": "EA",
#                     "quantity": 89,
#                     "unitPrice": 150.987,
#                     "netSale": 13303.46457,
#                     "totalSale": 13437.84300,
#                     "total": 14762.15667,
#                     "commercialDiscount": [
#                         34.37843,
#                         100.00
#                     ],
#                     "itemDiscount": [
#                         2.0,
#                         3.7
#                     ],
#                     "valueDifference": 6.0,
#                     "taxableItems": [
#                         {
#                             "taxType": "T1",
#                             "subType": "V009",
#                             "amount": 1863.32504,
#                             "rate": 14.0
#                         },
#                         {
#                             "taxType": "T4",
#                             "subType": "W001",
#                             "amount": 398.93294,
#                             "rate": 3.0
#                         }
#                     ]
#                 }
#             ],
#             "totalSales": 13532.343,
#             "totalCommercialDiscount": 135.89043,
#             "totalItemsDiscount": 9.6,
#             "extraReceiptDiscount": [
#                 25.49
#             ],
#             "netAmount": 13396.45257,
#             "feesAmount": 10.065,
#             "totalAmount": 14808.12859,
#             "taxTotals": [
#                 {
#                     "taxType": "T1",
#                     "amount": 1875.64336
#                 },
#                 {
#                     "taxType": "T4",
#                     "amount": 403.38734
#                 }
#             ],
#             "paymentMethod": "Cash",
#             "adjustment": 3.789,
#             "contractor": {
#                 "name": "contractor1",
#                 "amount": 2.563,
#                 "rate": 2.3
#             },
#             "beneficiary": {
#                 "amount": 20.569,
#                 "rate": 2.147
#             }
#         }


# def Serialize(json_object):
#     Serialize = ""
#     for key, value in json_object.items():
#         Serialize += "\"" + key + "\""
#         print('Key: ', key, 'Value: ', value)
#         if isinstance(value, list):
#             for rec in value:
#                 print('))))))))))))))))>', type(rec), rec)
#                 Serialize({})
#
# if isinstance(object, dict):
#     pass
#
# if isinstance(object, float):
#     pass

def _serialize_for_signing(eta_inv):
    if not isinstance(eta_inv, dict):
        return json.dumps(str(eta_inv), ensure_ascii=False)

    canonical_str = []
    for key, value in eta_inv.items():
        if not isinstance(value, list):
            canonical_str.append(json.dumps(key, ensure_ascii=False).upper())
            canonical_str.append(_serialize_for_signing(value))
        else:
            canonical_str.append(json.dumps(key, ensure_ascii=False).upper())
            for elem in value:
                canonical_str.append(json.dumps(key, ensure_ascii=False).upper())
                canonical_str.append(_serialize_for_signing(elem))
    return ''.join(canonical_str)


ser = _serialize_for_signing(receipt)
data = hashlib.sha256(ser.encode()).digest().hex()
print('=======>', ser)
print('=======>', data)
