# -*- coding: utf-8 -*-
"""
Copyright 2017 Bernard Giroux, Elie Dumas-Lefebvre, Jerome Simon
email: Bernard.Giroux@ete.inrs.ca

This file is part of BhTomoPy.

BhTomoPy is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import re
import numpy as np
from sqlalchemy import Column, String, Float, Boolean, SmallInteger, ForeignKey, Integer, PickleType
from utils import Base
from sqlalchemy import orm


class MogData(object):
    """
    Class to hold multi-offset gather (mog) data
    """

    def __init__(self, name='', date=None):
        self.ntrace      = 0     # number of traces
        self.nptsptrc    = 0     # number of points per trace
        self.rstepsz     = 0     # size of step used
        self.rnomfreq    = 0     # nominal frequency of antenna
        self.csurvmod    = ''    # survey mode
        self.timec       = 0     # the step of time data
        self.rdata       = 0     # raw data
        self.tdata       = None  # time data
        self.timestp     = 0     # matrix of range self.nptstrc containing all the time referencies
        self.Tx_x        = [0]   # x position of the transmitter
        self.Tx_y        = [0]   # y position of the transmitter
        self.Tx_z        = [0]   # z position of the transmitter
        self.Rx_x        = [0]   # x position of the receptor
        self.Rx_y        = [0]   # y position of the receptor
        self.Rx_z        = [0]   # z position of the receptor
        self.antennas    = ''    # name of the antenna
        self.synthetique = 0     # if 1 results from numerical modelling and 0 for field data
        self.tunits      = 0     # time units
        self.cunits      = ''    # coordinates units
        self.TxOffset    = 0     # length of he transmittor which is above the surface
        self.RxOffset    = 0     # length of he receptor which is above the surface
        self.comment     = ''    # is defined by the presence of any comment in the file
        self.date        = ''    # the date of the data sample
        self.name        = name

    def readRAMAC(self, basename):
        """
        loads data in Malå RAMAC format
        """
        rname = basename.split('/')
        rname = rname[-1]

        self.name = rname
        self.tunits = 'ns'
        self.cunits = 'm'

        self.readRAD(basename)
        self.readRD3(basename)
        try:
            self.readTLF(basename)
        except IOError as e:
            print(str(e) + ' [mog err1]')

        self.TxOffset = 0
        self.RxOffset = 0

        if not self.synthetique:

            if self.rnomfreq == 100.0:
                self.TxOffset = 0.665
                self.RxOffset = 0.665
            elif self.rnomfreq == 250.0:
                self.TxOffset = 0.325
                self.RxOffset = 0.365

        self.Tx_z = self.Tx_z[:self.ntrace]
        self.Rx_z = self.Rx_z[:self.ntrace]

        self.Tx_y = np.zeros(self.ntrace)
        self.Rx_y = np.zeros(self.ntrace)
        self.Tx_x = np.zeros(self.ntrace)
        self.Rx_x = np.zeros(self.ntrace)

    def readRAD(self, basename):
        """
        loads contents of Malå header file (*.rad extension)
        """
        try:
            file = open(basename, 'r')
        except:
            try:
                file = open(basename + ".rad", 'r')
            except:
                try:
                    file = open(basename + ".RAD", 'r')
                except Exception as e:
                    raise IOError("Cannot open RAD file '" + str(e)[:42] + "...' [mog 2]")

        # knowing the file's contents, we make sure to read every line while looking for keywords. When we've found one of
        # these keyword, we either search the int('\d+'), the float(r"[-+]?\d*\.\d+|\d+") or a str by getting the
        # needed information on the line

        # the search function returns 3 things, the type, the span (i.e. the index(es) of the element(s) that was(were) found)
        # and the group(i.e. the found element)

        lines = file.readlines()
        for line in lines:
            if "SAMPLES:" in line:
                self.nptsptrc = int(re.search('\d+', line).group())
            elif "FREQUENCY:" in line:
                self.timec = float(re.search(r"[-+]?\d*\.\d+|\d+", line).group())
            elif "OPERATOR:" in line:
                if 'MoRad' in line or 'syntetic' in line:
                    self.synthetique = True
                else:
                    self.synthetique = False
            elif "ANTENNAS:" in line:
                start, end = re.search('\d+', line).span()
                self.rnomfreq = float(line[start:end])
                self.antennas = line[9:].strip('\n')
            elif "LAST TRACE" in line:
                self.ntrace = int(re.search('\d+', line).group())

        self.timec = 1000.0 / self.timec
        self.timestp = self.timec * np.arange(self.nptsptrc)

        if not self.synthetique:
            self.antennas = self.antennas + "  - Ramac"

        file.close()
#         print(self.nptsptrc)
#         print(self.timec)
#         print(self.synthetique)
#         print(self.rnomfreq)
#         print(self.antennas)
#         print(self.ntrace)

    def readRD3(self, basename):
        """
        loads contents of *.rd3 extension
        RD3 stands for Ray Dream Designer 3 graphics
        """
        try:
            file = open(basename, 'rb')
        except:
            try:
                file = open(basename + ".rd3", 'rb')
            except:
                try:
                    file = open(basename + ".RD3", 'rb')
                except Exception as e:
                    raise IOError("Cannot open RD3 file '" + str(e)[:42] + "...' [mog 3]")

        self.rdata = np.fromfile(file, dtype='int16', count=self.nptsptrc * self.ntrace)
        self.rdata.resize((self.ntrace, self.nptsptrc))
        self.rdata = self.rdata.T

    def readTLF(self, basename):
        """
        loads contents of *.TLF extension
        """
        try:
            file = open(basename, 'r')
        except:
            try:
                file = open(basename + ".tlf", 'r')
            except:
                try:
                    file = open(basename + ".TLF", 'r')
                except Exception as e:
                    raise IOError("Cannot open TLF file '" + str(e)[:42] + "...' [mog 4]")
        self.Tx_z = np.array([])
        self.Rx_z = np.array([])
        lines = file.readlines()[1:]
        for line in lines:
            line_contents = re.findall(r"[-+]?\d*\.\d+|\d+", line)
            tnd          = int(line_contents[0])     # first trace
            tnf          = int(line_contents[1])     # last trace
            Rxd          = float(line_contents[2])   # first coordinate of the Rx
            Rxf          = float(line_contents[3])   # last coordinate of the Rx
            Tx           = float(line_contents[4])   # Tx's fixed position
            nt           = tnf - tnd + 1
            if nt == 1:
                dRx = 1
                if Rxd > Rxf:
                    Rxd = Rxf
            else:
                dRx = (Rxf - Rxd) / (nt - 1)

            vect = np.arange(Rxd, Rxf + dRx / 2, dRx)

            if nt > 0:
                self.Tx_z = np.append(self.Tx_z, (Tx * np.ones(np.abs(nt))))
                self.Rx_z = np.concatenate((self.Rx_z, vect))
        file.close()

    def readSEGY(self, basename):
        """
        :param basename:
        :return:
        """


class PruneParams(object):
    def __init__(self):
        self.stepTx = 0
        self.stepRx = 0
        self.round_factor = 0
        self.use_SNR = 0
        self.threshold_SNR = 0
        self.zmin = -1e99
        self.zmax = 1e99
        self.thetaMin = -90
        self.thetaMax = 90


class Mog(Base):  # Multi-Offset Gather

    __tablename__ = "Mog"
    name             = Column(String, primary_key=True)
    pruneParams      = Column(PickleType)    # Object holding the parameters used in pruning
    data             = Column(PickleType)    # Instance of MogData
    tau_params       = Column(PickleType)    # Parameters used to set source amplitude (set in manual_amp_ui)
    fw               = Column(PickleType)    # Numpy array holding wavelet transform frequency filtered traces (set in manual_*_ui)
    f_et             = Column(Float)         # Standard deviation on frequency
    amp_name_Ldc     = Column(String)        # Name of inversion to use in attenuation tomography (for obtaining matrix L)
    type             = Column(SmallInteger)  # VRP or cross-hole (0 or 1, respectively)  # TODO this is unused yet
    fac_dt           = Column(Float)         # Boolean: time step correction factor
    user_fac_dt      = Column(Float)         # Time step correction factor defined by user
    useAirShots      = Column(Boolean)       # Boolean holding whether or not AirShots are used
    TxCosDir         = Column(PickleType)    # Direction cosine at Tx points
    RxCosDir         = Column(PickleType)    # Direction cosine at Rx points

    ID               = Column(Integer)       # Unique ID for mog
    in_Rx_vect       = Column(PickleType)    # Indicates whether or not an element of the receiver is ignored  # TODO should be transferred to 'pruneParams'
    in_Tx_vect       = Column(PickleType)    # idem.
    in_vect          = Column(PickleType)    # idem.
    date             = Column(String)        # Date of the mog's data
    tt               = Column(PickleType)    # Arrival time
    et               = Column(PickleType)    # Standard deviation of arrival time
    tt_done          = Column(PickleType)    # Boolean indicator of arrival time

    ttTx             = Column(PickleType)    # Travel time picked at the Tx np.array
    ttTx_done        = Column(PickleType)    # Boolean indicator of the picked travel times

    amp_tmin         = Column(PickleType)    # Lower bound of amplitude analysis
    amp_tmax         = Column(PickleType)    # Upper bound of amplitude analysis
    amp_done         = Column(PickleType)    # Boolean indicator
    App              = Column(PickleType)    # Peak-to-peak amplitude
    fcentroid        = Column(PickleType)    # Centroid frequency
    scentroid        = Column(PickleType)    # Slowness for centroid frequency
    tauApp           = Column(PickleType)    # Pseudo travel times for peak-to-peak method
    tauApp_et        = Column(PickleType)    # Standard deviation
    tauFce           = Column(PickleType)    # Pseudo travel times for centroid frequency method
    tauFce_et        = Column(PickleType)    # Standard deviation
    tauHyb           = Column(PickleType)    # Pseudo travel times for an hybrid
    tauHyb_et        = Column(PickleType)    # Standard deviation
    Tx_z_orig        = Column(PickleType)    # Depth of Tx points (from borehole collar)
    Rx_z_orig        = Column(PickleType)    # Depth of Rx points (from borehole collar)

    Tx_name = Column(String, ForeignKey('Borehole.name'))    # One shouldn't manipulate these columns.
    Rx_name = Column(String, ForeignKey('Borehole.name'))    # Use the following Tx, Rx, av and ap instead.
    av_name = Column(String, ForeignKey('Airshots.name'))
    ap_name = Column(String, ForeignKey('Airshots.name'))
    Tx = orm.relationship("Borehole", foreign_keys=Tx_name)  # Mog's transmitter borehole
    Rx = orm.relationship("Borehole", foreign_keys=Rx_name)  # Mog's receiver borehole
    av = orm.relationship("AirShots", foreign_keys=av_name)  # Mog's 'before' airshot
    ap = orm.relationship("AirShots", foreign_keys=ap_name)  # Mog's 'after' airshot

    def __init__(self, name='', data=MogData()):
        self.pruneParams               = PruneParams()
        self.name                      = name
        self.data                      = data
        self.tau_params                = np.array([])
        self.fw                        = np.array([])
        self.f_et                      = 1
        self.amp_name_Ldc              = ''
        self.type                      = 0
        self.fac_dt                    = 1
        self.user_fac_dt               = 0
        self.pruneParams.stepTx        = 0
        self.pruneParams.stepRx        = 0
        self.pruneParams.round_factor  = 0
        self.pruneParams.use_SNR       = 0
        self.pruneParams.threshold_SNR = 0
        self.pruneParams.zmin          = -1e99
        self.pruneParams.zmax          = 1e99
        self.pruneParams.thetaMin      = -90
        self.pruneParams.thetaMax      = 90
        self.useAirShots               = False
        self.TxCosDir                  = np.array([])
        self.RxCosDir                  = np.array([])

        self.ID                       = Mog.getID()
        self.in_Rx_vect               = np.ones(self.data.ntrace, dtype=bool)
        self.in_Tx_vect               = np.ones(self.data.ntrace, dtype=bool)
        self.in_vect                  = np.ones(self.data.ntrace, dtype=bool)
        self.date                     = self.data.date
        self.tt                       = -1 * np.ones(self.data.ntrace, dtype=float)
        self.et                       = -1 * np.ones(self.data.ntrace, dtype=float)
        self.tt_done                  = np.zeros(self.data.ntrace, dtype=bool)

        if self.data.tdata is None:
            self.ttTx                 = np.array([])
            self.ttTx_done            = np.array([])
        else:
            self.ttTx                 = np.zeros(self.data.ntrace)
            self.ttTx_done            = np.zeros(self.data.ntrace, dtype=bool)

        self.amp_tmin                 = -1 * np.ones(self.data.ntrace, dtype=float)
        self.amp_tmax                 = -1 * np.ones(self.data.ntrace, dtype=float)
        self.amp_done                 = np.zeros(self.data.ntrace, dtype=bool)
        self.App                      = np.zeros(self.data.ntrace, dtype=float)
        self.fcentroid                = np.zeros(self.data.ntrace, dtype=float)
        self.scentroid                = np.zeros(self.data.ntrace, dtype=float)
        self.tauApp                   = -1 * np.ones(self.data.ntrace, dtype=float)
        self.tauApp_et                = -1 * np.ones(self.data.ntrace, dtype=float)
        self.tauFce                   = -1 * np.ones(self.data.ntrace, dtype=float)
        self.tauFce_et                = -1 * np.ones(self.data.ntrace, dtype=float)
        self.tauHyb                   = -1 * np.ones(self.data.ntrace, dtype=float)
        self.tauHyb_et                = -1 * np.ones(self.data.ntrace, dtype=float)
        self.Tx_z_orig                = self.data.Tx_z
        self.Rx_z_orig                = self.data.Rx_z

        self.pruneParams.zmin         = min(np.array([self.data.Tx_z, self.data.Rx_z]).flatten())
        self.pruneParams.zmax         = max(np.array([self.data.Tx_z, self.data.Rx_z]).flatten())

    def correction_t0(self, ndata, air_before, air_after):
        """
        :param ndata:
        :param air_before: instance of class Airshots
        :param air_after: instance of class Airshots
        """

#        show = False  # TODO
        fac_dt_av = 1
        fac_dt_ap = 1
        if not self.useAirShots:
            t0 = np.zeros(ndata)
            return t0, fac_dt_av, fac_dt_ap
        elif air_before.name == '' and air_after.name == '' and self.useAirShots:
            t0 = np.zeros(ndata)
            raise ValueError("t0 correction not applied; Pick t0 before and t0 after for correction")

        v_air = 0.2998
        t0av = np.array([])
        t0ap = np.array([])

        if air_before.name != '':
            if 'fixed_antenna' in air_before.method:
                t0av = self.get_t0_fixed(air_before, v_air)
            if 'walkaway' in air_before.method:
                pass  # TODO: get_t0_wa

        if air_after.name != '':
            if 'fixed_antenna' in air_before.method:
                t0ap = self.get_t0_fixed(air_after, v_air)

            if 'walkaway' in air_before.method:
                pass  # TODO: get_t0_wa

        if np.isnan(t0av) or np.isnan(t0ap):
            t0 = np.zeros((1, ndata))
            raise ValueError("t0 correction not applied;Pick t0 before and t0 after for correction")

        if np.all(t0av == 0) and np.all(t0ap == 0):
            t0 = np.zeros((1, ndata))
        elif t0av == 0:
            t0 = t0ap + np.zeros((1, ndata))
        elif t0ap == 0:
            t0 = t0av + np.zeros((1, ndata))
        else:
            dt0 = t0ap - t0av
            ddt0 = dt0 / (ndata - 1)
            t0 = t0av + ddt0 * np.arange(ndata)  # TODO pas sur de cette etape là

        return t0, fac_dt_av, fac_dt_ap

    @staticmethod
    def load_self(mog):
        Mog.getID(mog.ID)

    @staticmethod
    def get_t0_fixed(shot, v):
        times = shot.tt
        std_times = shot.et
        ind = np.where(times != -1.0)[0]
        if np.all(std_times == -1.0):
            times = np.mean(times[ind])
        else:
            times = sum(times[ind] * std_times[ind]) / sum(std_times[ind])
        t0 = times - float(shot.d_TxRx[0]) / v
        return t0

    @staticmethod
    def getID(*args):
        nargin = len(args)
        counter = 0
        if nargin == 1:
            if counter == 0:
                counter = args[1]
            elif counter < args[1]:
                counter = args[1]
        if counter == 0:
            counter = 1
        else:
            counter += 1

        ID = counter
        return ID

    def getCorrectedTravelTimes(self):

        if self.data.synthetique == 1:
            tt = self.tt
            t0 = np.zeros(np.shape(tt))
            return tt, t0

        t0, fac_dt_av, fac_dt_ap = self.correction_t0(len(self.tt), self.av, self.ap)

        if self.av is not None:
            self.av.fac_dt = fac_dt_av

        if self.ap is not None:
            self.ap.fac_dt = fac_dt_ap

        if self.user_fac_dt == 0:
            if fac_dt_av != 1 and fac_dt_ap != 1:
                self.fac_dt = 0.5 * (fac_dt_av + fac_dt_ap)
            elif fac_dt_av != 1:
                self.fac_dt = fac_dt_av
            elif fac_dt_ap != 1:
                self.fac_dt = fac_dt_ap
            else:
                self.fac_dt = 1

        t0 = self.fac_dt * t0
        tt = self.fac_dt * self.tt - t0

        return tt, t0


class AirShots(Base):

    __tablename__ = "Airshots"
    name    = Column(String, primary_key=True)
#     mog     = Column(PickleType)  # Deprecated ?
    data    = Column(PickleType)  # MogData instance
    d_TxRx  = Column(PickleType)  # Distance between Tx and Rx
    fac_dt  = Column(Float)       # Time step correction factor computed from slope of t vs d
    method  = Column(String)      # 'fixed_antenna' when single distance value between Tx & Rx or 'walkaway' when multiple distances
    tt      = Column(PickleType)  # Arrival times
    et      = Column(PickleType)  # Standard deviation of arrival times
    tt_done = Column(PickleType)  # Boolean indicator for arrival times

    def __init__(self, name='', data=MogData()):
        self.mog = Mog()
        self.name = name
        self.data = data
        self.d_TxRx = 0
        self.fac_dt = 1

        self.tt = -1 * np.ones((1, self.data.ntrace), dtype=float)
        self.et = -1 * np.ones((1, self.data.ntrace), dtype=float)
        self.tt_done = np.zeros((1, self.data.ntrace), dtype=bool)


if __name__ == '__main__':

    m = Mog('M01')
    md = MogData()
    md.readRAMAC('testData/formats/ramac/t0102')
    m.data = md
