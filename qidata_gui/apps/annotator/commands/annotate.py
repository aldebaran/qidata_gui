from ..app import QiDataApp

class AnnotateCommand:
    @staticmethod
    def run(args):
        qidata_app = QiDataApp(args.path)
        try:
            qidata_app.run()
        except KeyboardInterrupt:
            pass