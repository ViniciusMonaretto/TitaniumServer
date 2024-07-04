from apps.app_manager import AppManager
from modules.modules_manager import ModulesManager
from middleware.middleware import Middleware


if __name__ == "__main__":
    middleware = Middleware()

    app_manager = AppManager( middleware )
    modules_manager = ModulesManager( middleware )
    
    app_manager.run()
    modules_manager.run()

    app_manager.join()
    modules_manager.join()
