
from enum import Enum
class DocumentStatus(str, Enum):
    SIGNED = "SIGNED"
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    DRAFT = "DRAFT"  # 
    




class RecipientRole(str, Enum):
    SIGNER= "SIGNER",
    APPROVER = "APPROVER",
    CC="CC"
    VIEWER= "VIEWER"


# export const FieldType= {
#     "SIGNATURE":"SIGNATURE",
#     "NAME":"NAME",
#     "INITIALS":"INITIALS",
#     "EMAIL":"EMAIL",
#     "NUMBER":"NUMBER",
#     "RADIO":"RADIO",
#     "CHECKBOX":"CHECKBOX",
#     "DROPDOWN":"DROPDOWN",
#     "DATE":"DATE",
#     "TEXT":"TEXT",
#     "FREE_SIGNATURE":"FREE_SIGNATURE"
# }
 


 