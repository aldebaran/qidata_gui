from ..app import AnnotationMakerApp

class AnnotateCommand:
    @staticmethod
    def run(args):
        qidata_app = AnnotationMakerApp(args.path)
        try:
            qidata_app.run()
        except KeyboardInterrupt:
            pass