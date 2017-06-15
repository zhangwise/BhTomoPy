# -*- coding: utf-8 -*-
"""
Created on Mon Aug 29 08:09:12 2016

@author: giroux

Copyright 2017 Bernard Giroux, Jerome Simon
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

from PyQt5 import QtWidgets, QtCore
import os
import database
from mog import Mog
from model import Model


def chooseMOG(module, filename=None):
    d = QtWidgets.QDialog()

    l0 = QtWidgets.QLabel(parent=d)
    l0.setAlignment(QtCore.Qt.AlignCenter)
    l0.setStyleSheet('background-color: white')

    b0 = QtWidgets.QPushButton("Choose Database", d)
    b1 = QtWidgets.QPushButton("Ok", d)
    b2 = QtWidgets.QPushButton("Cancel", d)

    b3 = QtWidgets.QComboBox(d)

    l0.move(10, 10)
    b0.move(10, 40)
    b1.setMinimumWidth(b2.width())
    b2.setMinimumWidth(b1.minimumWidth())
    b0.setMinimumWidth(10 + 2 * b1.minimumWidth())
    l0.setMinimumWidth(10 + 2 * b1.minimumWidth())
    b3.setMinimumWidth(2 * b1.minimumWidth())

    b3.move(15, 70)

    b2.move(10, 100)
    b1.move(20 + b1.minimumWidth(), 100)

    def cancel():
        nonlocal d
        d.done(0)

    def ok():
        nonlocal d
        d.done(1)

    def choose_db():
        nonlocal d
        nonlocal l0
        nonlocal b3
        filename = QtWidgets.QFileDialog.getOpenFileName(d, 'Choose Database')[0]
        if filename:
            if filename.find('.db') != -1:

                database.load(module, filename)
                l0.setText(os.path.basename(filename))
                load_mogs()

            else:
                QtWidgets.QMessageBox.warning(b3, '', 'Database not in *.db format',
                                              QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.NoButton,
                                              QtWidgets.QMessageBox.NoButton)
                l0.setText('')

    def load_mogs():
        nonlocal b3
        nonlocal l0
        b3.clear()
        mogs = module.session.query(Mog).all()
        if mogs:
            for mog in mogs:
                b3.addItem(mog.name)
        else:
            QtWidgets.QMessageBox.warning(b3, '', 'File does not contain MOGS.',
                                          QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.NoButton,
                                          QtWidgets.QMessageBox.NoButton)
            l0.setText('')

    if str(module.engine.url) != 'sqlite:///:memory:':
        l0.setText(database.short_url(module))
        load_mogs()
    else:
        l0.setText('')

    b1.clicked.connect(ok)
    b2.clicked.connect(cancel)
    b0.clicked.connect(choose_db)

    d.setWindowTitle("Choose MOG")
    d.setWindowModality(QtCore.Qt.ApplicationModal)

    isOk = d.exec_()

    if isOk == 1:
        mog_no = b3.currentIndex()
        if mog_no != -1:
            return module.session.query(Mog).filter(Mog.name == str(b3.currentText())).first()


def chooseModel(module, filename=None):
    d = QtWidgets.QDialog()

    l0 = QtWidgets.QLabel(parent=d)
    l0.setAlignment(QtCore.Qt.AlignCenter)
    l0.setStyleSheet('background-color: white')

    b0 = QtWidgets.QPushButton("Choose Database", d)
    b1 = QtWidgets.QPushButton("Ok", d)
    b2 = QtWidgets.QPushButton("Cancel", d)

    b3 = QtWidgets.QComboBox(d)

    l0.move(10, 10)
    b0.move(10, 40)
    b1.setMinimumWidth(b2.width())
    b2.setMinimumWidth(b1.minimumWidth())
    b0.setMinimumWidth(10 + 2 * b1.minimumWidth())
    l0.setMinimumWidth(10 + 2 * b1.minimumWidth())
    b3.setMinimumWidth(2 * b1.minimumWidth())

    b3.move(15, 70)

    b2.move(10, 100)
    b1.move(20 + b1.minimumWidth(), 100)

    def cancel():
        nonlocal d
        d.done(0)

    def ok():
        nonlocal d
        d.done(1)

    def choose_db():
        nonlocal d
        nonlocal l0
        nonlocal b3
        if save_warning(module):
            filename = QtWidgets.QFileDialog.getOpenFileName(d, 'Choose Database')[0]
            if filename:
                if filename.find('.db') != -1:

                    database.load(module, filename)
                    l0.setText(os.path.basename(filename))
                    load_models()

                else:
                    QtWidgets.QMessageBox.warning(b3, '', 'Database not in *.db format',
                                                  QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.NoButton,
                                                  QtWidgets.QMessageBox.NoButton)
                    l0.setText('')

    def load_models():
        nonlocal b3
        nonlocal l0

        b3.clear()
        models = module.session.query(Model).all()
        if models:
            for model in models:
                b3.addItem(model.name)
        else:
            QtWidgets.QMessageBox.warning(b3, '', 'File does not contain Models.',
                                          QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.NoButton,
                                          QtWidgets.QMessageBox.NoButton)
            l0.setText('')

    if str(module.engine.url) != 'sqlite:///:memory:':
        l0.setText(database.short_url(module))
        load_models()
    else:
        l0.setText('')

    b1.clicked.connect(ok)
    b2.clicked.connect(cancel)
    b0.clicked.connect(choose_db)

    d.setWindowTitle("Choose Model")
    d.setWindowModality(QtCore.Qt.ApplicationModal)
    isOk = d.exec_()

    if isOk == 1:
        model_no = b3.currentIndex()
        if model_no != -1:
            return module.session.query(Model).filter(Model.name == str(b3.currentText())).first()


def save_warning(module):
    if module.modified:  # if any data has been modified, warn the user. Otherwise, proceed.
        d = QtWidgets.QDialog()

        l0 = QtWidgets.QLabel(parent=d)
        l0.setAlignment(QtCore.Qt.AlignCenter)

        b0 = QtWidgets.QPushButton("Save", d)
        b1 = QtWidgets.QPushButton("Save as", d)
        b2 = QtWidgets.QPushButton("Discard changes", d)
        b3 = QtWidgets.QPushButton("Cancel", d)

        l0.move(10, 10)
        b0.setMinimumWidth(b2.width())
        b1.setMinimumWidth(b2.width())
        b2.setMinimumWidth(b2.width())
        b3.setMinimumWidth(b2.width())
        b0.move(15, 40)
        b1.move(15 + b2.width(), 40)
        b2.move(15 + 2 * b2.width(), 40)
        b3.move(15 + 3 * b2.width(), 40)
        l0.setMinimumWidth(10 + 4 * b2.width())
        d.setMaximumWidth(10 * 3 + b2.width() * 4)
        d.setMaximumHeight(10 * 2 + b2.height() * 2)
        d.setMinimumWidth(10 * 3 + b2.width() * 4)
        d.setMinimumHeight(10 * 2 + b2.height() * 2)

        l0.setText("You must save your database before proceeding.")

        d.setWindowTitle("Warning")
        d.setWindowModality(QtCore.Qt.ApplicationModal)

        def save():
            nonlocal d
            d.done(1)

        def save_as():
            nonlocal d
            d.done(2)

        def no_save():
            nonlocal d
            d.done(3)

        def cancel():
            nonlocal d
            d.done(0)

        b0.clicked.connect(save)
        b1.clicked.connect(save_as)
        b2.clicked.connect(no_save)
        b3.clicked.connect(cancel)

        ok = d.exec_()
        if ok == 0:
            ok = False
        elif ok == 1:
            ok = savefile(module)
        elif ok == 2:
            ok = saveasfile(module)
        elif ok == 3:
            module.modified = False
            ok = True

        return ok  # returns False if action has to be reverted. Returns True otherwise.

    else:
        return True


def savefile(module):

    try:
        if str(module.engine.url) == 'sqlite:///:memory:':
            return saveasfile(module)

        module.session.commit()
        QtWidgets.QMessageBox.information(None, 'Success', "Database was saved successfully",
                                          buttons=QtWidgets.QMessageBox.Ok)
        module.modified = False
        return True

    except Exception as e:
        QtWidgets.QMessageBox.warning(None, 'Warning', "Database could not be saved : " + str(e),
                                      buttons=QtWidgets.QMessageBox.Ok)

    return False


def saveasfile(module):
    filename = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Database as ...', filter='Database (*.db)', )[0]

    if filename:
        if os.path.basename(filename) != database.long_url(module):
            database.save_as(module, filename)
            module.modified = False
            return True

        else:
            module.session.commit()
            QtWidgets.QMessageBox.information(None, 'Success', "Database was saved successfully",
                                              buttons=QtWidgets.QMessageBox.Ok)
            module.modified = False
            return True

    return False


def auto_create_scrollbar(widget):
    """
    Adds a scrollbar to a widget. The scrollbar appears IF NEEDED. The returned scrollbar
    object is the one that must then be manipulated (i.e. not the sent widget).
    """
    scrollbar = QtWidgets.QScrollArea()
    scrollbar.setWidget(widget)
    scrollbar.setWidgetResizable(True)

    desired_min_height = widget.sizeHint().height()
    desired_min_width = widget.sizeHint().width()

    screen_resolution = QtWidgets.QApplication.desktop().screenGeometry()
    width, height = screen_resolution.width(), screen_resolution.height()

    if desired_min_height > 4 / 5 * height:  # sets a threshold that limits the size of the widget. 4 / 5 is an arbitrary
        desired_min_height = 4 / 5 * height  # number accounting for the menu bar and the scroll bar.

    if desired_min_width > 4 / 5 * width:
        desired_min_width = 4 / 5 * width

    scrollbar.setMinimumWidth(desired_min_width)
    scrollbar.setMinimumHeight(desired_min_height)

    return scrollbar


def duplicate_verif(string, string_list):
    """
    Returns wether or not there is a duplicate in a list with some additional feedback.
    """
    if not string:
        QtWidgets.QMessageBox.warning(None, "Warning", "Could not rename: field must not be empty.")
        return True

    if string in string_list:
        QtWidgets.QMessageBox.warning(None, "Warning", "Could not rename: this name already exists.")
        return True

    return False


def duplicate_new_name(string, string_list):
    """
    Verifies if a string has a duplicate in a list and returns a new string in such cases.
    """
    if not string:
        raise ValueError

    recursion = 1

    while string in string_list:
        if recursion != 1:
            string = string[:-2]
        string += ' ' + str(recursion)
        recursion += 1

    return string
