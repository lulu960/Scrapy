# settings.py

BOT_NAME = 'myproject'

SPIDER_MODULES = ['myproject.spiders']
NEWSPIDER_MODULE = 'myproject.spiders'

# ⚠️ Important : se faire passer pour un vrai navigateur
DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36',
    'Accept-Language': 'fr',
}

# 📉 Atténuer la fréquence des requêtes
DOWNLOAD_DELAY = 1.5  # Délai de 1.5 seconde
RANDOMIZE_DOWNLOAD_DELAY = True  # Variabiliser les délais

# 🚦 AutoThrottle pour s’adapter dynamiquement
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1.5
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# 🔄 Réduire les redirections (peut être désactivé si utile)
# REDIRECT_ENABLED = False

# 🔒 Gérer les cookies (si nécessaires pour le site)
COOKIES_ENABLED = True

# 📊 Log niveau
LOG_LEVEL = 'INFO'

# 🛑 Fermer automatiquement après X pages (pour tester)
# CLOSESPIDER_PAGECOUNT = 100
