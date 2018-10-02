from django.views.generic import TemplateView, RedirectView


class IndexView(RedirectView):
    url = "/group/"


class GroupListView(TemplateView):
    template_name = "group_list.html"

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        stuff = [
            "Bedfordshire, Luton and Milton Keynes",
            "Bristol, North Somerset and South Gloucestershire STP",
            "Buckinghamshire Integrated Care System",
            "Greater Manchester Health and Social Care Partnership",
 #            "Herefordshire and Worcestershire STP",
#            "Lancashire and South Cumbria STP",
            "Sussex and East Surrey STP",
            "West, North and East Cumbria STP"
        ]
        ctx["object_list"] = [
            dict(
                display_name=o,
                url="organisation/lutan/governance/"
            ) for o in stuff
        ]
        return ctx


