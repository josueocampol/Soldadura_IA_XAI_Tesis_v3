from monai_label_app import MONAILabelApp

class MyApp(MONAILabelApp):
    def __init__(self, app_dir, conf=None):
        super().__init__(app_dir, conf)

    def get_app_name(self):
        return "MyApp"
	
    def get_description(self):
        return "Mi primera app de MONAI Label"

if __name__ == "__main__":
    app = MyApp("C:\\Users\\Usuario\\Documents\\JOSUE\\TG2\\MONAILabel_Apps")
    app.run()