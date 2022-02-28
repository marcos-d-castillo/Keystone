from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from flask import request, jsonify
from flask_cors import cross_origin

from app.api import bp


tzDict = {
    "Auckland (UTC+12:00)": "Pacific/Auckland",
    "Guadalcanal (UTC+11:00)": "Pacific/Guadalcanal",
    "Vladivostok (UTC+10:00)": "Asia/Vladivostok",
    "Tokyo (UTC+9:00)": "Asia/Tokyo",
    "Hong Kong (UTC+8:00)": "Asia/Hong_Kong",
    "Jakarta (UTC+7:00)": "Asia/Jakarta",
    "Dhaka (UTC+6:00)": "Asia/Bishkek",
    "Karachi (UTC+5:00)": "Asia/Karachi",
    "Dubai (UTC+4:00)": "Asia/Dubai",
    "Addis Ababa (UTC+3:00)": "Africa/Addis_Ababa",
    "Cairo (UTC+2:00)": "Africa/Cairo",
    "Casablanca (UTC+1:00)": "Africa/Casablanca",
    "Abidjan (UTC+0:00)": "Africa/Abidjan",
    "Cape Verde (UTC-1:00)": "Atlantic/Cape_Verde",
    "Noronha (UTC-2:00)": "America/Noronha",
    "Buenos Aires (UTC-3:00)": "America/Argentina/Buenos_Aires",
    "Caracas (UTC-4:00)": "America/Caracas",
    "EST (UTC-5:00)": "America/New_York",
    "CST (UTC-6:00)": "America/Chicago",
    "MST (UTC-7:00)": "America/Denver",
    "PST (UTC-8:00)": "America/Los_Angeles",
    "Alaska (UTC-9:00)": "America/Sitka",
    "Hawaii (UTC-10:00)": "Pacific/Honolulu",
    "Samoa (UTC-11:00)": "Pacific/Samoa"
}


@bp.route('/datetime', methods=['GET', 'POST'])
@cross_origin()
def get_datetime():
    r = request.get_json()
    sec = int(r['datetime'])
    dt = datetime.fromtimestamp(sec, tz=timezone.utc)

    convertedDt = dt.astimezone(ZoneInfo(tzDict[r['targetTimezone']]))

    res = {
        'datetime': convertedDt.isoformat()
    }

    return jsonify(res)


@bp.route('/timezones', methods=['GET'])
@cross_origin()
def get_timezones():

    return jsonify(tzDict)
