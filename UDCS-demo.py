# Author: Joey Press, Abdu Sallouh, and Gregory Smith
# A subsystem used for the University's Clinics
class Clinics:
    class Clinic:
        def __init__(self, name, students={}):
            self.name = name
            self.capacity = 0
            self.students = students
            self.appointments = []
            self.schedule = None

        class Appointment:
            def __init__(self, patientID, student):
                self.patientID = patientID
                self.student = student

            def addDate(self, date):
                self.date = str(date)

            def addTime(self, time):
                self.date = self.date + '/' + time

        class Schedule:
            def __init__(self, timings={}):
                self.timings = timings

            def updateSchedule(self, appointment):
                for timings in self.timings[appointment.student][appointment.date.split('/')[0]]:
                    for time in timings.keys():
                        if appointment.date.split('/')[-1] == time:
                            timings[time] = appointment


            def getTimings(self, student):
                aTimings = {}

                for studentK in self.timings.keys():
                    if studentK == student:
                        for day in self.timings[student]:
                            if self.timings[student][day]:
                                aTimings[day] = []
                                for timings in self.timings[student][day]:
                                    for time in timings:
                                        if timings[time] is None and day in aTimings:
                                            aTimings[day].append(time)
                                    if day in aTimings and not aTimings[day]:
                                       del aTimings[day]
                if aTimings == {}:
                    return None
                else:
                    return aTimings

            # For admin use only, not neccesary for the project
            def buildSchedule(self):
                pass

        def lookupPatient(self, patientID):
            for student in self.students.keys():
                for patient in self.students[student][0]:
                    if patientID == patient:
                        if self.students[student][1] == False:
                            return student
                        else:
                            return None
            return None

        def assignPatient(self, patientID):
            student = self.getMinStudent()
            self.students[student].append(patientID)
            self.capacity += 1
            return student

        def getMinStudent(self):

            mini = 4
            for student in self.students:
                if len(self.students[student]) < mini and self.students[student][1] == False:
                    mini = len(self.students[student])
                    self.mStudent = student
            return self.mStudent

        def addAppointment(self, appointment):
            self.appointments.append(appointment)
            self.schedule.updateSchedule(appointment)
            self.students[appointment.student][1] = self.updateStudentStatus(appointment.student)

        def getTimings(self, studentID):
            return self.schedule.getTimings(studentID)

        def updateStudentStatus(self, student):
            for day in self.schedule.timings[student]:
                for hour in self.schedule.timings[student][day]:
                    for status in hour:
                        if hour[status] is None:
                            return False
            return True

    class Port:

        def __init__(self):
            self.pClinic = Clinics.Clinic
            self.pClinics = self.clinics()

        def clinics(self):
            clinics = [
                self.pClinic('ITU', {'Joseph Press': [[8373, 3223], False], 'Abdu Sallouh': [[2324, ], False]}),
                self.pClinic('Oral Medicine', {'Ayah Almehiri': [[2324], False]}),
                self.pClinic('Oral Surgery', {'Adam Smith': [[], False]}),
            ]

            clinics[0].schedule = clinics[0].Schedule(
                {'Joseph Press': {'mon': [{'8:00am': None}, {'12:00pm': None}], 'tue': [{'1:00pm': None}], 'wed': [],
                                  'fri': [{'4:00pm': None}], 'sat': [], 'sun': []},
                 'Abdu Sallouh': {'mon': [], 'tue': [{'10:00am': None}], 'wed': [{'5:00pm': None}], 'fri': [],
                                  'sat': [{'10:00am': None}], 'sun': []}},
            )
            clinics[1].schedule = clinics[1].Schedule(
                {'Ayah Almehiri':
                     {'mon': [{'7:00pm': None}], 'tue': [], 'wed': [], 'fri': [], 'sat': [{'6:00pm': None}],
                      'sun': [{'6:00pm': None}]}},
            )
            clinics[2].schedule = clinics[2].Schedule(
                {'Adam Smith':
                     {'mon': [], 'tue': [{'9:00pm': None}], 'wed': [], 'fri': [{'3:00pm': None}, {'6:00pm': None}],
                      'sat': [], 'sun': [{'5:00pm': None}]}},
            )

            return clinics

        CAPACITY = 20  # spcifies the total capacity for each clinic
        SCAPACITY = 4  # specifies the total capacity for each student in a given week
        tAppointment = None  # a temporary reference to an appointment

        def matchCLinic(self, clinic):
            for sClinic in self.pClinics:
                if sClinic.name == clinic:
                    return sClinic

        def getClinicNames(self):
            names = []
            for clinic in self.pClinics:
                names.append(clinic.name)
            return names

        def checkCapacityFull(self, clinic):
            if clinic.capacity == self.CAPACITY:
                return True
            else:
                return False

        def checkAssigned(self, patientID, clinic):
            return clinic.lookupPatient(patientID)

        def assignPatient(self, patientID, clinic):
            return clinic.assignPatient(patientID)

        def createAppointment(self, clinic, patientID, studentID):
            return clinic.Appointment(patientID, studentID)

        def getTimings(self, clinic, studentID):
            return clinic.getTimings(studentID)

        def saveAppointment(self, clinic, appointment):
            return clinic.addAppointment(appointment)

        # For setting students by admin, not required for now
        def setStudents(self, students):
            pass


# Class used as a facade for the system
class Controller:
    c = Clinics()
    p = c.Port()

    def __init__(self, userID):
        self.patientID = userID
        self.tClinic = None  # a temporary reference to a clinic object
        self.tAppointment = None  # a temporary reference to an appointment object
        self.studentID = None
        self.sAppointments = []

    def requestClinics(self):
        return self.p.getClinicNames()

    def clnicSelected(self, clinic):
        cObj = self.p.matchCLinic(clinic)
        self.tClinic = cObj
        if self.p.checkCapacityFull(cObj):
            UI.showUnavaliability()
        else:
            self.tClinic = cObj
            self.studentID = self.p.checkAssigned(self.patientID, cObj)
            if not self.studentID:
                self.studentID = self.p.assignPatient(self.patientID, cObj)
            return self.p.getTimings(cObj, self.studentID)

    def dateSelected(self, date, day):
        self.tAppointment = self.p.createAppointment(self.tClinic, self.patientID, self.studentID)
        self.tAppointment.addDate(day)
        return date[day]

    def timeSelected(self, time):
        self.tAppointment.addTime(time)
        return [self.tAppointment.date.split('/')[0], self.tAppointment.date.split('/')[1], self.tAppointment.student]

    def confirmAppointment(self):
        self.sAppointments.append([self.tClinic.name,self.tAppointment])
        return self.p.saveAppointment(self.tClinic, self.tAppointment)


class UI:
    con = Controller(1234)

    def __init__(self):
        self.showClnics()

    def showClnics(self):
        print()
        lst = self.con.requestClinics()
        print('Please select one of the clinics below:')
        for i, v in enumerate(lst):
            print(i + 1, ' ', v)
        choice = int(input()) - 1
        return self.showDates(self.con.clnicSelected(lst[choice]))

    def showDates(self, dates):
        if dates is None:
            self.showUnavaliability()
        else:
            print()
            # Adapted from: https://stackoverflow.com/questions/19216334/python-give-start-and-end-of-week-data-from-a-given-date
            ###########################################
            from datetime import datetime, date, timedelta

            day = str(date.today())
            dt = datetime.strptime(day, '%Y-%m-%d')
            start = dt - timedelta(days=dt.weekday())

            ############################################

            from enum import Enum

            class Dates(Enum):
                mon = 0
                tue = 1
                wed = 2
                thu = 3
                fri = 4
                sat = 5
                sun = 6

            lst = []
            for day in dates.keys():
                if len(dates[day]) > 0:
                    lst.append(day)

            print('Select a date:')
            for i, v in enumerate(lst):
                print(f'{i + 1} {v} {str(start + timedelta(getattr(Dates, v).value))[:-9]}')
            choice = int(input()) - 1
            return self.showTimes(self.con.dateSelected(dates, lst[choice]))

    def showTimes(self, times):
        print()
        lst = []
        for time in times:
                lst.append(time)

        print('Select a time:')
        for i, v in enumerate(lst):
            print(i + 1, ' ', v)
        choice = int(input()) - 1
        return self.showSummary(self.con.timeSelected(lst[choice]))

    def showSummary(self, summary):
        print()
        # Adapted from: https://stackoverflow.com/questions/19216334/python-give-start-and-end-of-week-data-from-a-given-date
        ###########################################
        from datetime import datetime, date, timedelta

        day = str(date.today())
        dt = datetime.strptime(day, '%Y-%m-%d')
        start = dt - timedelta(days=dt.weekday())

        ############################################

        from enum import Enum

        class Dates(Enum):
            mon = 0
            tue = 1
            wed = 2
            thu = 3
            fri = 4
            sat = 5
            sun = 6

        print('Appointment Summary:')
        print('Date: ', summary[0], ' ', str(start + timedelta(getattr(Dates, summary[0]).value))[:-9])
        print('Time: ', summary[1])
        print('Student: ', summary[2])
        print()
        input('Press enter to confirm')
        self.con.confirmAppointment()
        return self.showSuccess()

    def showUnavaliability(self):
        print()
        print('Clinic Capacity Full.. Try again later')
        self.showAppointments()

    def showSuccess(self):
        print()
        print('Appointment booked successfully')

        print('Would you like to book another appointment? Y/n')
        inp = input()
        if inp == 'Y':
            self.showClnics()
        elif inp == 'n':
            self.showAppointments()


    def showAppointments(self):
        print()
        # Adapted from: https://stackoverflow.com/questions/19216334/python-give-start-and-end-of-week-data-from-a-given-date
        ###########################################
        from datetime import datetime, date, timedelta

        day = str(date.today())
        dt = datetime.strptime(day, '%Y-%m-%d')
        start = dt - timedelta(days=dt.weekday())

        ############################################

        from enum import Enum

        class Dates(Enum):
            mon = 0
            tue = 1
            wed = 2
            thu = 3
            fri = 4
            sat = 5
            sun = 6

        print('These are the appointments that you booked:')
        for i, appointments in enumerate(self.con.sAppointments,1):
            print(i, '.')
            print('Clinic:', appointments[0])
            print('Date: ', appointments[1].date.split('/')[0], ' ', ' ', str(start + timedelta(getattr(Dates, appointments[1].date.split('/')[0]).value))[:-9])
            print('Time: ', appointments[1].date.split('/')[1])
            print('Student: ', appointments[1].student)
            
        print()
        input('Press any key to exit')

##Start of the main prograwm
UI()
