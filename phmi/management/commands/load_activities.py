from phmi import models
from django.db import transaction
from django.core.management.base import BaseCommand, CommandError


IMPLIED = "Implied or explicit consent"
SET_ASIDE = "Set aside as data will be de-identified"

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
        "CCG": [
            "DUTY: Promote integration",
            "DUTY: To prepare Joint Strategic Needs Assessments",
            "DUTY: To work with local authorities to improve the well-being of young children",
            "POWER: To commission certain other health services"
        ],
        "NHS England": [
            "DUTY: Provide integrated services to improve outcomes and reduce inequalities",
            "DUTY: To ensure health services are provided in an integrated way",
            "DUTY: To exercise relevant public health functions",
        ]
    },
    ACT_2: {
        "CCG": [
            "POWER: To conduct research"
        ],
        "NHS England": [
            "DUTY: To put and keep in place arrangements to monitor and improve the quality of health care",
            "POWER: To conduct research",
        ]
    },
    ACT_3: {
        "CCG": [
            "DUTY: Exercise its functions effectively, efficiently and economically",
            "DUTY: Improving quality of services",
            "DUTY: Promote integration",
        ],
        "NHS England": [
            "DUTY: Provide integrated services to improve outcomes and reduce inequalities",
            "DUTY: To ensure health services are provided in an integrated way",
            "DUTY: To exercise relevant public health functions",
        ]
    },
    ACT_4: {
        "CCG": [
            "DUTY: Promote integration",
            "DUTY: To prepare Joint Strategic Needs Assessments",
            "DUTY: To work with local authorities to improve the well-being of young children",
        ],
        "NHS England": [
            "DUTY: Provide integrated services to improve outcomes and reduce inequalities",
            "DUTY: To ensure health services are provided in an integrated way",
            "DUTY: To exercise relevant public health functions",
        ]
    },
    ACT_5: {
        "Acute Trust": [
            "DUTY: NHS bodies to co-operate",
            "POWER: NHS Foundation Trusts authorised to provide healthcare",
        ],
        "Local Authority": [
            "PROVIDER DUTY: Provide services to improve public health",
            "PROVIDER DUTY: To carry out functions with the aim of integrating services"
        ],
        "Mental Health Trust": [
            "PROVIDER DUTY: Provide services to improve public health",
            "PROVIDER DUTY: To carry out functions with the aim of integrating services"
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


