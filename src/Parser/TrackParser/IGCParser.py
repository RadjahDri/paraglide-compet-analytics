from Parser.TrackParser.TrackParser import TrackParser
from Track import Track
from GpsPoint import GpsPoint
from TrackPoint import TrackPoint

import datetime
import re

### CONSTANTS
RE_DATE_LINE = re.compile("HFDTEDATE:([0-9]{2})([0-9]{2})([0-9]{2})\n")
RE_PILOT_NAME_LINE = re.compile("HFPLTPILOT:(.*)\n")
RE_GPS_REFERENCE_LINE = re.compile("HFDTM100GPSDATUM:(.*)\n")
RE_B_LINE = re.compile("B([0-9]{2})([0-9]{2})([0-9]{2})(.{2})(.{5})([N|S])(.{3})(.{5})([W|E])[A|V](.{5})(.{5})\n")

### CLASSES
class IGCParser(TrackParser):
    def parse(self):
        date = None
        pilotName = None
        gpsReference = None
        coordinates = []

        with open(self.filePath) as inputFile:
            line = inputFile.readline()
            while(line):
                if(line.startswith("HFDTEDATE")):
                    match = RE_DATE_LINE.match(line)
                    if(not match):
                        raise RuntimeError("Parsing failed: HFDTEDATE is not valid")
                    date = datetime.date(int(match.group(3))+2000, int(match.group(2)), int(match.group(1)))

                elif(line.startswith("HFPLTPILOT")):
                    match = RE_PILOT_NAME_LINE.match(line)
                    if(not match):
                        raise RuntimeError("Parsing failed: HFPLTPILOT is not valid")
                    pilotName = match.group(1)

                elif(line.startswith("HFDTM100GPSDATUM")):
                    match = RE_GPS_REFERENCE_LINE.match(line)
                    if(not match):
                        raise RuntimeError("Parsing failed: HFDTM100GPSDATUM is not valid")
                    gpsReference = match.group(1)

                elif(line.startswith("B")):
                    trackPoint = self.parseBLine(line)
                    coordinates.append(trackPoint)

                line = inputFile.readline()

        track = Track(pilotName, date, gpsReference, coordinates)
        return track


    def parseBLine(self, line):
        match = RE_B_LINE.match(line)
        if(not match):
            raise RuntimeError("Parsing failed: B entry is not valid: %s" % line)

        time = datetime.time(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        latDegrees = int(match.group(4))
        latMinutes = float(match.group(5)) / 1000

        lonDegrees = int(match.group(7))
        lonMinutes = float(match.group(8)) / 1000
        alt = int(match.group(10))

        gpsPoint = GpsPoint.fromDegreesMinutes((latDegrees, latMinutes, match.group(6)), (lonDegrees, lonMinutes, match.group(9)))
        trackPoint = TrackPoint(time, gpsPoint, alt)
        return trackPoint