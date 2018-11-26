from phmi import models
from django.db import transaction
from django.core.management.base import BaseCommand, CommandError


IMPLIED = "Implied consent/reasonable expectations"
SET_ASIDE = "Set aside as data will be de-identified for this purpose"


ACT_1 = ("Allocating risk scores and stratifying populations \
for specified future adverse events causing poor health outcomes \
to individuals", SET_ASIDE,)

ACT_2 = ("Identifying and managing research cohorts", SET_ASIDE,)

ACT_3 = (
    "Managing quality of health and care services (inc. clinical audit)",
    SET_ASIDE,
)

ACT_4 = ("Reviewing, evaluating and transforming current health and care \
service provision across and within populations", SET_ASIDE,)


ACT_5 = (
    "Systematically selecting impactible individuals within \
risk-stratified population cohorts for early intervention or prevention",
    IMPLIED
)


data = {
    ACT_1: {
        "Local Authority": [
            "COMMISSIONER POWER: To provide preventative services"
        ],
        "NHS England": [
            "DUTY: To exercise relevant public health functions",
            "POWER: To assist SoS in providing health services and exercising public health functions",

        ]
    },
    ACT_2: {
        "CCG": [
            "DUTY: To promote the involvement of each patient"
            "DUTY: Research",
            "DUTY: Public and patient involvement",
            "POWER: To conduct research",
        ],
        "NHS England": [
            "DUTY: Public and patient involvement",
            "POWER: To conduct research",
        ],
        "Local Authority": [
            "COMMISSIONER POWER: To conduct research",
            "COMMISSIONER DUTY:  To ensure the involvement of local people in decision-making",
        ],

    },
    ACT_3: {
        "CCG": [
            "DUTY: Arrangement of personal health budgets",
        ],
        "NHS England": [
            "POWER: To make payments to CCGs in respect of quality of services",
            "DUTY: Co-operation with social services regarding the provision of NHS continuing healthcare",
            "DUTY: Arrangement of personal health budgets",
        ],
        "Local Authority": [
            "COMMISSIONER DUTY: To make direct payments to meet care needs",
            "COMMISSIONER DUTIES: Social care (various)",
            "COMMISSIONER POWER: To make direct payments to patients",
        ],
    },
    ACT_4: {
        "CCG": [
            "POWER: To make direct payments to patients",
            "DUTY: To promote the involvement of each patient",
            "DUTY: Public and patient involvement",
            "DUTY: To work with local authorities regarding adoption services",
            "DUTY: To consider the economic, social and environmental benefits to be achieved through commissioning"
        ],
        "NHS England": [
            "DUTY: Public and patient involvement",
            "DUTY: To collect and analyse information relating to safety of services",
            "DUTY: To consider the economic, social and environmental benefits to be achieved through commissioning",
        ],
        "Local Authority": [
            "COMMISSIONER DUTY: To prepare a joint strategic needs assessment",
            "COMMISSIONER DUTY:  To ensure the involvement of local people in decision-making",
            "COMMISSIONER DUTY: To consider the economic, social and environmental benefits to be achieved through commissioning"
        ]
    },
    ACT_5: {
        "Local Authority": [
            "PROVIDER POWER: To provide preventative services",
            "PROVIDER DUTIES: Social care (various)"
        ],
        "NHS Trust": [
            "DUTY: Provision of NHS goods and services"
        ],
        "Independent Sector": [
            "DUTY (NHS Trust Only): Provision of NHS goods and services"
        ]
    }
}


class Command(BaseCommand):
    help = "Load in some activities"

    @transaction.atomic
    def handle(self, *args, **options):
        for activity_details, org_type_dict in data.items():
            activity, _ = models.Activity.objects.get_or_create(
                name=activity_details[0],
                duty_of_confidence=activity_details[1]
            )
            for org_type_name, justifications in org_type_dict.items():
                if not models.OrgType.objects.filter(
                    name__startswith=org_type_name
                ).exists():
                    import ipdb; ipdb.set_trace()
                org_type = models.OrgType.objects.get(
                    name__startswith=org_type_name
                )

                legal_mapping, _ = models.LegalMapping.objects.get_or_create(
                    activity=activity, org_type=org_type
                )
                for justification_name in justifications:
                    justification, _ = models.LegalJustification.objects.get_or_create(
                        name=justification_name
                    )
                    legal_mapping.justification.add(justification)


