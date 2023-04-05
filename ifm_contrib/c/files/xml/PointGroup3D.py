__author__ = 'are'

class PointGroup3D:
    groupName = "3D Point Group"
    points = []
    offset = (0.0, 0.0)
    fileName = None

    def __init__(self, filename=None):
        pass

    def LoadFrom(self, filename):
        file = open(filename)
        pass  # to be implemented
        file.close()

    def SaveTo(self, filename):

        # Defintion of templates for XML file output:

        template_header = \
'''<?xml version="1.0" encoding="utf-8" standalone="no" ?>
<data_array version="1">
    <title>%GRPNAME%</title>
    <column_header column="0">x</column_header>
    <column_header column="1">y</column_header>
    <column_header column="2">z</column_header>
    <array rows="%LEN%" columns="3" type="double" unitClass="LENGTH" units="[m]">
'''
        template_line = \
'''        <row nr="%No%">%x%  %y%  %z%</row>
'''
        template_footer = \
'''    </array>
</data_array>
<offsets unitClass="LENGTH" units="[m]">
    <offset value="%OFFX%" />
    <offset value="%OFFY%" />
</offsets>
'''
        # END template Definition

        # Write file from template strings:

        file = open(filename, "w")
        file.write(template_header.
                   replace("%GRPNAME%", self.groupName).
                   replace("%LEN%", str(len(self.points))))

        for p in self.points:
            file.write(template_line.
                   replace("%No%", str(self.points.index(p)+1)).
                   replace("%x%", p[0]).
                   replace("%y%", p[1]).
                   replace("%z%", p[2]))

        file.write(template_footer.
                   replace("%OFFX%", str(self.offset[0])).
                   replace("%OFFY%", str(self.offset[1])))

        file.close()