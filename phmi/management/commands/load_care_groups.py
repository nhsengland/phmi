from django.core.management.base import BaseCommand
from django.db import transaction

from phmi import models

data = {
    ("Cheshire and Merseyside Health and Care Partnership", "Susta",): [
        "Aintree University Hospital NHS Foundation Trust",
        "Alder Hey Children's NHS Foundation Trust",
        "Bridgewater Community Healthcare NHS Foundation Trust",
        "Cheshire and Wirral Partnership NHS Foundation Trust",
        "Cheshire East Council",
        "Cheshire West & Chester Cou",
        "Countess of Chester Hospital NHS Foundation Trust",
        "East Cheshire NHS Trust",
        "Eastern Cheshire CCG",
        "Halton BC (Unitary)",
        "Halton CCG",
        "Knowsley CCG",
        "Knowsley MBC",
        "Liverpool CCG",
        "Liverpool City Council",
        "Liverpool Community Health NHS Trust",
        "Liverpool Heart and Chest Hospital NHS Foundation Trust",
        "Liverpool Women's NHS Foundation Trust",
        "Mersey Care NHS Foundation Trust",
        "Mid Cheshire Hospitals NHS Foundation Trust",
        "North West Ambulance Service NHS Trust",
        "North West Boroughs Healthcare NHS Foundation Trust",
        "Royal Liverpool and Broadgreen University Hospitals NHS Trust",
        "Sefton Council",
        "South Cheshire CCG",
        "Southport And Formby CCG",
        "Southport and Ormskirk Hospital NHS Trust",
        "South Sefton CCG",
        "St Helens and Knowsley Hospital Services NHS Trust",
        "St Helens CCG",
        "St Helens MBC",
        "The Clatterbridge Cancer Centre NHS Foundation Trust",
        "The Walton Centre NHS Foundation Trust",
        "Vale Royal CCG",
        "Warrington and Halton Hospitals NHS Foundation Trust",
        "Warrington BC (Unitary)",
        "Warrington CCG",
        "West Cheshire CCG",
        "Wirral CCG",
        "Wirral Community NHS Foundation Trust",
        "Wirral MBC",
        "Wirral University Teaching Hospital NHS Foundation Trust",
    ],
    ("Humber, Coast and Vale", "Sust"): [
        "CARE PLUS GROUP",
        "East Midlands Ambulance Service NHS Trust",
        "East Riding Of Yorkshire CCG",
        "East Riding of Yorkshire Co",
        "FOCUS INDEPENDENT ADULT SOCIAL WORK C.I.C",
        "Hull and East Yorkshire Hospitals NHS Trust",
        "Hull CCG",
        "Humber NHS Foundation Trust",
        "Kingston-Upon-Hull City Cou",
        "NAVIGO",
        "North East Lincolnshire CCG",
        "North East Lincolnshire Cou",
        "Northern Lincolnshire and Goole NHS Foundation Trust",
        "North Lincolnshire CCG",
        "North Lincolnshire Council",
        "Rotherham Doncaster and South Humber NHS Foundation Trust",
        "Scarborough And Ryedale CCG",
        "Tees, Esk and Wear Valleys NHS Foundation Trust",
        "Vale Of York CCG",
        "York City Council",
        "Yorkshire Ambulance Service NHS Trust",
        "YORKSHIRE HEALTHCARE PARTNERS LTD",
        "York Teaching Hospital NHS Foundation Trust",
    ],
    ("Nottinghamshire", "Integrated care system",): [
        "Mansfield And Ashfield CCG",
        "Newark And Sherwood CCG",
        "Nottingham City CCG",
        "Nottingham City Council",
        "Nottingham North And East CCG",
        "Nottinghamshire CC",
        "Nottinghamshire Healthcare NHS Foundation Trust",
        "Nottingham University Hospitals NHS Trust",
        "Nottingham West CCG",
        "Rushcliffe CCG",
        "Sherwood Forest Hospitals NHS Foundation Trust",
    ],
    ("South Yorkshire and Bassetlaw", "Sust"): [
        "Barnsley CCG",
        "Barnsley Hospital NHS Foundation Trust",
        "Barnsley MBC",
        "Bassetlaw CCG",
        "Bassetlaw District Council",
        "Chesterfield Royal Hospital NHS Foundation Trust",
        "Doncaster and Bassetlaw Teaching Hospitals NHS Foundation Trust",
        "Doncaster CCG",
        "East Midlands Ambulance Service NHS Trust",
        "Nottinghamshire CC",
        "Nottinghamshire Healthcare NHS Foundation Trust",
        "Rotherham CCG",
        "Rotherham Doncaster and South Humber NHS Foundation Trust",
        "Rotherham MBC",
        "Sheffield CCG",
        "Sheffield Children's NHS Foundation Trust",
        "Sheffield City Council",
        "Sheffield Health & Social Care NHS Foundation Trust",
        "Sheffield Teaching Hospitals NHS Foundation Trust",
        "South West Yorkshire Partnership NHS Foundation Trust",
        "The Rotherham NHS Foundation Trust",
        "Yorkshire Ambulance Service NHS Trust",
    ]
}


class Command(BaseCommand):
    help = "Load in some basic care groups"

    @transaction.atomic
    def handle(self, *args, **options):
        for care_system_details, organisations in data.items():
            care_system_name = care_system_details[0]
            group_type_prefix = care_system_details[1]
            group_type = models.GroupType.objects.get(
                name__startswith=group_type_prefix
            )

            care_system, _ = models.CareSystem.objects.get_or_create(
                name=care_system_name,
                type=group_type
            )

            for organisation_name in organisations:
                organisation, _ = models.Organisation.objects.get_or_create(
                    name=organisation_name
                )
                care_system.orgs.add(organisation)
