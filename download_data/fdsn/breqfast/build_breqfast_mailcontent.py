"""
mail content sent by breqfast.
"""
import sh
import obspy
import pandas as pd

template = """.NAME ziyixi
.INST Michigan State University
.MAIL CMSE, MSU, East Lansing, MI, 48824
.EMAIL ziyixi@mail.ustc.edu.cn
.PHONE 517 505-0802
.FAX   517 505-0802
.MEDIA FTP
.ALTERNATE MEDIA 1/2" tape - 6250
.ALTERNATE MEDIA EXABYTE
.LABEL {label}
.SOURCE ~NEIC PDE~Jan 1990 PDE~National Earthquake Information Center - USGS DOI~
.HYPO ~{year} {month} {day} {hour} {minute} {second}~ {latitude}~ {longitude}~{depth}~18~216~{region}~
.MAGNITUDE ~{magnitude}~mw~
.QUALITY B
.END
{station_information}
"""


def create_mail_contents():
    mail_list = []
    events = obspy.read_events("./Japan_slab/*")
    sh.mkdir("-p", "./mails_ziyixi")

    stations = pd.read_csv(
        "./fdsn_stations",
        sep="\s+",
        names=["station", "network", "lat", "lon", "elv", "dep"],
    )

    for item in events:
        station_information = ""
        starttime = item.origins[0].time - 2 * 60
        endtime = item.origins[0].time + 40 * 60
        for index, row in stations.iterrows():
            station_information += f"{row.station} {row.network} {starttime.year} {starttime.month} {starttime.day} {starttime.hour} {starttime.minute} {round(starttime.second + (1e-6) * starttime.microsecond,2)} {endtime.year} {endtime.month} {endtime.day} {endtime.hour} {endtime.minute} {round(endtime.second + (1e-6) * endtime.microsecond,2)} 2 BH? HH?\n"

        mail_content = template.format(
            label=item.origins[0].resource_id.id.split("/")[2],
            year=item.origins[0].time.year,
            month=item.origins[0].time.month,
            day=item.origins[0].time.day,
            hour=item.origins[0].time.hour,
            minute=item.origins[0].time.minute,
            second=round(
                item.origins[0].time.second +
                (1e-6) * item.origins[0].time.microsecond,
                2,
            ),
            latitude=item.origins[0].latitude,
            longitude=item.origins[0].longitude,
            depth=item.origins[0].depth / 1000,
            region=item.origins[0].region,
            magnitude=item.magnitudes[0].mag,
            station_information=station_information,
        )

        with open(f"./mails_ziyixi/{item.origins[0].resource_id.id.split('/')[2]}", "w") as f:
            f.write(mail_content)


if __name__ == "__main__":
    create_mail_contents()
