import csv
from phmi import models
from django.db import transaction
from django.core.management.base import BaseCommand, CommandError


IMPLIED = "Implied consent/reasonable expectations"
SET_ASIDE = "Set aside as data will be de-identified for this purpose"


ACTIVITY_1 = ("Allocating risk scores and stratifying populations \
for specified future adverse events causing poor health outcomes \
to individuals", SET_ASIDE,)

ACTIVITY_2 = ("Identifying and managing research cohorts", SET_ASIDE,)

ACTIVITY_3 = (
    "Managing quality of health and care services (inc. clinical audit)",
    SET_ASIDE,
)

ACTIVITY_4 = ("Reviewing, evaluating and transforming current health and care \
service provision across and within populations", SET_ASIDE,)


ACTIVITY_5 = (
    "Systematically selecting impactible individuals within \
risk-stratified population cohorts for early intervention or prevention",
    IMPLIED
)

ACTIVITY_6 = (
    "General provision of population health management", IMPLIED
)



data = {
    ACTIVITY_1: {
        "Local Authority": [
            "Commissioner Power: To provide preventative services",
        ],
        "NHS England": [
            "Duty: To exercise relevant public health functions",
            "Power: To assist SoS in providing health services and \
exercising public health functions",
        ]
    },
    ACTIVITY_2: {
        "CCG": [
            "Duty: To promote the involvement of each patient",
            "Duty: Research",
            "Duty: Public and patient involvement",
            "Power: To conduct research",
        ],
        "NHS England": [
            "Duty: Public and patient involvement",
            "Power: To conduct research",
        ],
        "Local Authority": [
            "Commissioner Power: To conduct research",
            "Commissioner Duty:  To ensure the involvement of local people in decision-making",
        ],

    },
    ACTIVITY_3: {
        "CCG": [
            "Duty: Arrangement of personal health budgets",
        ],
        "NHS England": [
            "Power: To make payments to CCGs in respect of quality of services",
            "Duty: Co-operation with social services regarding the provision \
of NHS continuing healthcare",
            "Duty: Arrangement of personal health budgets",
        ],
        "Local Authority": [
            "Commissioner Duty: To make direct payments to meet care needs",
            "Commissioner Duties: Social care (various)",
            "Commissioner Power: To make direct payments to patients",
        ],
    },
    ACTIVITY_4: {
        "CCG": [
            "Power: To make direct payments to patients",
            "Duty: To promote the involvement of each patient",
            "Duty: Public and patient involvement",
            "Duty: To work with local authorities regarding adoption services",
            "Duty: To consider the economic, social and environmental benefits \
to be achieved through commissioning"
        ],
        "NHS England": [
            "Duty: Public and patient involvement",
            "Duty: To collect and analyse information relating to safety of \
services",
            "Duty: To consider the economic, social and environmental benefits to be achieved through commissioning",
        ],
        "Local Authority": [
            "Commissioner Duty: To prepare a joint strategic needs assessment",
            "Commissioner Duty:  To ensure the involvement of local people in \
decision-making",
            "Commissioner Duty: To consider the economic, social and \
environmental benefits to be achieved through commissioning"
        ]
    },
    ACTIVITY_5: {
        "Local Authority": [
            "PROVIDER Power: To provide preventative services",
            "PROVIDER Duties: Social care (various)",
        ],
        "NHS Trust": [
            "Duty: Provision of NHS goods and services",
        ],
    },
    ACTIVITY_6: {
        "NHS England": [
            "Duty: To promote a comprehensive health service",
            "Power:  To do anything that will facilitate the discharge of \
functions under the 2006 Act",
            "Duty: To exercise functions efficiently",
            "Duty: To secure continuous improvement in the quality of services",
            "Duty:  To reduce health inequalities",
            "Duty: To promote integrated health services",
            "Duty: To promote integration between health services and \
health-related services",
            "Duty: To promote innovation",
            "Power: To obtain and analyse data",
            "Duty: Eliminate discrimination, harassment and victimisation \
and advance equality of opportunity",
            "Duty:  To share information",
        ],
        "CCG": [
            "Power:  To do anything that will facilitate the discharge of \
functions under the 2006 Act",
            "Power: To assist Secretary of State in providing health services \
and exercising public health functions",
            "Duty:  To exercise any functions delegated to the CCG by the \
Secretary of State",
            "Duty: Exercise its functions efficiently",
            "Duty: Securing continuous improvement in quality of services \
provided to individuals",
            "Duty: Reduce health inequalities",
            "Duty: To promote innovation",
            "Duty: to promote integrated health services",
            "Duty: to promote integration between health services and \
health-related services",
            "Power: For a CCG to deliver services jointly with another CCG",
            "Power: For a CCG to deliver services jointly with a combined \
authority",
            "Power: For NHS England to deliver CCG services instead of or \
jointly with a CCG",
            "Duty: To make CCG facilities available to local authorities ",
            "Power: To obtain and analyse data",
            "Duty: To co-operate with local authorities",
            "Duty:  To co-operate with NHS bodies when delivering care \
functions",
            "Duty: Eliminate discrimination, harassment and victimisation and \
advance equality of opportunity",
            "Duty:  To share information",
            "Power: Be partnership organisations",
            "Power:  To partner with local authorities",
        ],
        "Local Authority": [
            "Duty:  To promote individual wellbeing",
            "Duty: To carry out functions with the aim of integrating services",
            "Duty:  To co-operate with NHS bodies when delivering care functions",
            "Duty:  To meet the care and support needs of eligible adults",
            "Power:  To meet the care and support needs of eligible adults",
            "Duty:  To meet the support needs of eligible carers",
            "Power:  To meet the support needs of eligible carers",
            "Duty: To improve the well-being of and reduce inequalities for children",
            "Duty: Eliminate discrimination, harassment and victimisation and advance equality of opportunity",
            "Duty:  To share information",
            "Power:  General Power",
            "Duty:  To exercise any functions delegated to the local authority by the Secretary of State",
            "Duty:  To make services available to NHS bodies",
            "Duty: To co-operate with CCGs and NHS England",
            "Power: To obtain and analyse data",
        ],
        "NHS Trust": [
            "Duty (NHS Trust Only): Provision of NHS goods and services",
            "Duty (NHS Trust Only): Efficient delivery of functions",
            "Duty: NHS bodies to co-operate ",
            "Power (NHS Trust Only): General Power",
            "Power (NHS Trust Only): Joint exercise of functions",
            "Duty: Eliminate discrimination, harassment and victimisation and advance equality of opportunity",
            "Duty: To share information",
            "Power: Be partnership organisations",
        ]
    }
}


class Command(BaseCommand):
    help = "Load in some activities"

    def parse_name(self, some_name):
        allowed_prefixes = ["Duty", "Power", "Duties"]
        try:
          prefix, suffix = some_name.split(":", 1)
        except ValueError:
          print(some_name)
          raise
        for allowed_prefix in allowed_prefixes:
            if allowed_prefix in prefix:
                return f"{allowed_prefix.strip()}: {suffix.strip()}"
        raise ValueError(f"Unable to parse {some_name}")

    def create_activities(self, activitiy, org_type, names):
        """
        Looks up for similar names in the statutes csvs.

        Notably the names above are more details for example they
        have things such as COMISSIONER Duties rather than just
        Duties as it would be called in the statutes.

        As a result we have to do some fiddling to make them
        match up.

        We can't just use the suffix as for some suffixes there is both
        a Duty and a Power
        """
        file_name = "data/csvs/statutes/{}.csv".format(
            org_type.name.lower().replace(" ", "-")
        )
        count = 0

        names_to_original_names = {self.parse_name(i): i for i in names}
        name_to_statute = {}
        with open(file_name) as f:
            reader = csv.reader(f)
            for i in reader:
                try:
                    justification = self.clean_justification(i[1])
                except:
                    import ipdb; ipdb.set_trace()
                    raise
                if not justification:
                    continue
                dict_name = self.parse_name(justification)
                if dict_name in name_to_statute:
                    raise ValueError(f"Duplicate of {dict_name} in {file_name}")
                name_to_statute[dict_name] = i[2]

        for name, original_name in names_to_original_names.items():
            if name not in name_to_statute:
                raise ValueError(f"Unable to find {name} in {file_name}")

            justification, created = models.LegalJustification.objects.get_or_create(
                name=original_name,
                statute=name_to_statute[name],
                org_type=org_type
            )
            justification.activities.add(activitiy)

            if created:
                count += 1
        return count

    def clean_justification(self, justification):
        if "(NHS FT Only)" in justification:
            return
        return justification.replace("(NHS Trust Only)", "")

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Deleting all activities and legal justifications")
        models.Activity.objects.all().delete()
        models.LegalJustification.objects.all().delete()
        self.stdout.write("Starting import")
        total = 0
        for activity_details, org_type_dict in data.items():
            activity, _ = models.Activity.objects.get_or_create(
                name=activity_details[0],
                duty_of_confidence=activity_details[1]
            )
            for org_type_name, justifications in org_type_dict.items():
                justifications = [
                    self.clean_justification(i) for i in justifications
                ]
                justifications = [i for i in justifications if i]

                org_type = models.OrgType.objects.get(
                    name__startswith=org_type_name
                )
                total += self.create_activities(
                    activity, org_type, justifications
                )

        self.stdout.write(f"Saving {total} legal justifications")



