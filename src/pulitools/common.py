#!/usr/bin/python2.6
# -*- coding: utf8 -*-

"""
"""
__author__      = "Jérôme Samson"
__copyright__   = "Copyright 2014, Mikros Image"

import os
import datetime

# from datetime import datetime
import numpy as np

from PyQt4.QtCore import qDebug
from PyQt4.QtGui import QColor, QTextCursor

def roundTime(dt=None, roundTo=60):
  """Round a datetime object to any time laps in seconds
  dt : datetime.datetime object, default now.
  roundTo : Closest number of seconds to round to, default 1 minute.
  Author: Thierry Husson 2012 - Use it as you want but don't blame me.
  """
  if dt == None : dt = datetime.datetime.now()
  seconds = (dt - dt.min).seconds

  rounding = (seconds+roundTo/2) // roundTo * roundTo
  return dt + datetime.timedelta(0,rounding-seconds,-dt.microsecond)


def lowerQuartile(src):
  """
  [15, 15, 14, 13, 14, 14, 15, 15, 14, 13],
  13 13 14 14 14 14 15 15 15 15
  0  1  2  3  4  5  6  7  8  9
        q1          q2
  """
  res = []
  sortedSrc = np.sort(src)
  for i,col in enumerate(sortedSrc):
      res.append( col[len(col)/4] )
  return res

def higherQuartile(src):
  """
  """
  res = []
  sortedSrc = np.sort(src)
  for i,col in enumerate(sortedSrc):
    q1 = col[(len(col)/4)]
    q2 = col[3*(len(col)/4)]
    print "q1=%d q2 = %d for %r" % (q1, q2, col)
    res.append(q2)
  return res




class XLogger():
  """
  Simple log formatter.
  """

  def debug(self,text):
    qDebug( str(datetime.datetime.now().strftime("%m-%d %H:%M:%S")) + " - " + str(text) )
    pass
  def info(self,text):
    print str(datetime.datetime.now().strftime("%m-%d %H:%M:%S")) + " - " + str(text)
  def warning(self,text):
    print str(datetime.now().strftime("%m-%d %H:%M:%S")) + " - WARNING - " + str(text)
  def error(self,text):
    qDebug( str(datetime.datetime.now().strftime("%m-%d %H:%M:%S")) + " - ERROR - " + str(text) )
    print str(datetime.datetime.now().strftime("%m-%d %H:%M:%S")) + " - ERROR - "+ str(text)


class OutLog:
    def __init__(self, edit, out=None, color=None):
        """(edit, out=None, color=None) -> can write stdout, stderr to a
        QTextEdit.
        edit = QTextEdit
        out = alternate stream ( can be the original sys.stdout )
        color = alternate color (i.e. color stderr a different color)
        """
        self.edit = edit
        self.out = out
        self.color = color

    def write(self, m):
        if self.color:
            tc = self.edit.textColor()
            self.edit.setTextColor(self.color)

        self.edit.moveCursor(QTextCursor.End)
        self.edit.insertPlainText( m )

        if self.color:
            self.edit.setTextColor(tc)

        if self.out:
            self.out.write(m)
