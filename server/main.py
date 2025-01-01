from apps.app_manager import AppManager
from modules.modules_manager import ModulesManager
from middleware.middleware import Middleware
from services.services_management import ServiceManager


if __name__ == "__main__":
    middleware = Middleware()

    app_manager = AppManager( middleware )
    modules_manager = ModulesManager( middleware )
    service_manager = ServiceManager( middleware )
    
    app_manager.run()
    modules_manager.run()
    service_manager.run()

    app_manager.join()
    modules_manager.join()
    service_manager.join()
