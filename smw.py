# -*- coding: utf-8 -*-
"""
Created on Tue Sep 18 13:13:12 2018

@author: d0s
"""
import visa
import instrument


class Smw(instrument.Inst):
    def __init__(self, addr = 'ASRL1::INSTR', backend = '@sim'):
        super().__init__(addr, backend)
        self.cf = 0
        self.sumRate = 0
        self.reflvl = -200
        self.alpha = 0

