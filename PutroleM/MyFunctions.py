import yaml
import datetime


def reload_settings():
    with open('Settings.yaml', 'r') as file:
        Settings = yaml.safe_load(file)
    return Settings


def update_settings(key, value):
    with open('Settings.yaml', 'r') as file:
        settings = yaml.safe_load(file)

    settings[key] = value

    with open('Settings.yaml', 'w') as file:
        yaml.dump(settings, file)


def decrement_attempts():
        with open('Settings.yaml') as file:
            settings = yaml.load(file, Loader=yaml.FullLoader)
        
        # Récupérer le nombre de tentatives
        nombre_tentatives = settings['number of attempts']
        
        # Décrémenter le nombre de tentatives
        nombre_tentatives = nombre_tentatives - 1 if nombre_tentatives > 0 else 0
        
        # Mettre à jour le fichier YAML avec la nouvelle valeur
        settings['number of attempts'] = nombre_tentatives
        
        with open('Settings.yaml', 'w') as file:
            yaml.dump(settings, file)


def save_user_info(sub_info):
    with open('Log.txt', 'a') as file:
        file.write(f"{sub_info['id']}   {sub_info['pseudo']}    {sub_info['date_role']}\n")


def add_user_to_file(ctx):
    sub_info = {'id': ctx.author.id, 'pseudo': ctx.author.name, 'date_role': str(datetime.date.today())}
    save_user_info(sub_info)


def remove_passwords_from_yaml_file(file_path):
    with open(file_path, 'r') as file:
        settings = yaml.safe_load(file)
        if settings and settings.get('Valid passwords'):
            settings['Valid passwords'] = []
        with open(file_path, 'w') as file:
            yaml.dump(settings, file)


def remove_expirate_date():
    Settings = reload_settings()
    if 'expirate date' in Settings:
        with open('Settings.yaml', 'r') as file:
            Settings = yaml.safe_load(file)
            del Settings['expirate date']
        with open('Settings.yaml', 'w') as file:
            yaml.dump(Settings, file)