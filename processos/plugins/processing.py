# -*- coding: utf-8 -*-

# QvProcessPlugin
processingClass = None

class QvProcessingRun:

    @staticmethod
    def run(name, params):
        print("RUN processing", name)
        try:
            if processingClass.canceled(): return None
            if processingClass is None: return None
            if processingClass.canceled(): return None
            return processingClass.run(name, params)
        except Exception as e:
            print(str(e))
            return None

processing = QvProcessingRun
