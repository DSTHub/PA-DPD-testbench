#interface SpecAnalyzer
import instrument
import abc

class ISpecAnalyzer(instrument.Inst, abc.ABC):
    def __init__(self):
        super().__init__()
